from scheduler import add_to_queue, save_daily
import os
import json
import google.generativeai as genai
from rss_reader import get_latest_news
from modules import (
    load_text,
    load_json,
    validate_json,
    send_telegram,
    send_poll
)
print("=" * 50)
print("🍞 Starting CatLoaf AI Bakery V2")
print("=" * 50)

# --------------------------------------------------
# Load Configuration
# --------------------------------------------------

config = load_json("config.json")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not GEMINI_API_KEY:
    raise Exception("Missing GEMINI_API_KEY")

if not TELEGRAM_TOKEN:
    raise Exception("Missing TELEGRAM_BOT_TOKEN")

if not TELEGRAM_CHAT_ID:
    raise Exception("Missing TELEGRAM_CHAT_ID")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

print("✓ Configuration Loaded")

# --------------------------------------------------
# Load Prompt Files
# --------------------------------------------------

brand = load_text("brand.txt")

prompt_template = load_text("prompt.txt")

history = load_text("history.txt")

print("✓ Prompt Loaded")

# --------------------------------------------------
# Load News
# --------------------------------------------------

print("Fetching RSS...")

articles = get_latest_news()

seen = set()

news_items = []

for article in articles:

    title = article.get("title", "").strip()

    if not title:
        continue

    key = title.lower()

    if key in seen:
        continue

    seen.add(key)

    news_items.append(title)

articles = articles[:12]
news_text = "\n\n".join(
    f"Title: {a['title']}\nSummary: {a.get('summary', '')}"
    for a in articles
 )
print(f"✓ {len(news_items)} News Articles Loaded")

# --------------------------------------------------
# Build Prompt
# --------------------------------------------------

prompt = f"""
{brand}

{prompt_template}
"""

prompt = (
    prompt
    .replace("{news}", news_text)
    .replace("{history}", history)
)

print("✓ Prompt Built")

# --------------------------------------------------
# Generate Response
# --------------------------------------------------

generation_config = {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

response = model.generate_content(
    prompt,
    generation_config=generation_config
)

if not hasattr(response, "text") or not response.text:
    raise Exception("Gemini returned an empty response.")

print("✓ Gemini Response Received")

print("=" * 50)
print(response.text)
print("=" * 50)

data = validate_json(response.text)

print("✓ JSON Validated")

save_daily(data)
print("✓ Daily content saved")

add_to_queue(data)
print("✓ Saved to Queue")

# --------------------------------------------------
# Telegram Message Builder
# --------------------------------------------------

def divider():
    return "━━━━━━━━━━━━━━━━━━━━━━"


messages = []

message_types = []

# --------------------------------------------------
# X POSTS
# --------------------------------------------------

x_text = f"""
🐦 <b>CATLOAF X POSTS</b>

{divider()}
"""

for post in data["x_posts"]:

    x_text += f"""

🔥 <b>{post["type"].title()}</b>

{post["content"]}
"""

messages.append(x_text.strip())
message_types.append("x_posts")

# --------------------------------------------------
# TELEGRAM POST
# --------------------------------------------------

tg = data["telegram"]

telegram_message = f"""
🔥 <b>TODAY'S HOT LOAF</b>

{divider()}

🍞 <i>Fresh from today's oven...</i>

{tg["opening"]}

🔥 <b>Fresh Alpha</b>

"""

for bullet in tg["bullets"]:
    telegram_message += f"\n• {bullet}"

telegram_message += f"""

🧈 <b>Why It's Hot</b>

{tg["why"]}

🥖 <b>Hot Take</b>

{tg["question"]}

{divider()}
🍞 Stay Cozy.
🐱 @CatLoafCoin
"""

messages.append(telegram_message.strip())
message_types.append("hot_loaf")

# --------------------------------------------------
# MEME
# --------------------------------------------------

meme = data["meme"]

meme_message = f"""
🎨 <b>$CLOAF ART OF THE DAY</b>

{divider()}

🖼 <b>Image Prompt</b>

{meme["template"]}

🎭 <b>Scene</b>

{meme["scene"]}

💬 <b>Caption</b>

{meme["caption"]}

🤣 <b>Why It Works</b>

{meme["why"]}
"""

messages.append(meme_message.strip())
message_types.append("art")

# --------------------------------------------------
# ENGAGEMENT
# --------------------------------------------------

# --------------------------------------------------
# POLL
# --------------------------------------------------

messages.append(data["poll"]["question"])
message_types.append("what_if")

# --------------------------------------------------
# BEST TIME
# --------------------------------------------------

best = data["best_time"]

best_message = f"""
🕒 <b>BEST TIME TO POST</b>

{divider()}

⏰ {best["utc"]}

🌍 {best["reason"]}

🎯 {best["audience"]}
"""

messages.append(best_message.strip())
message_types.append("best_time")

print(f"✓ Built {len(messages)} Telegram Messages")

# --------------------------------------------------
# Compact History
# --------------------------------------------------

fingerprint = json.dumps(
    data.get("history", {}),
    ensure_ascii=False
)

entries = [
    line
    for line in history.splitlines()
    if line.strip()
]

entries.append(fingerprint)

entries = entries[-10:]

with open("history.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(entries))

print("✓ History Updated")
"""
# --------------------------------------------------
# Send Telegram Messages
# --------------------------------------------------

print("\nSending Telegram messages...\n")

sent = 0
failed = 0

for index, (message, msg_type) in enumerate(zip(messages, message_types), start=1):

    if not message.strip():
        print(f"Skipping empty message #{index}")
        continue

    if msg_type not in ["hot_loaf", "art", "what_if"]:
        print(f"Skipping internal message: {msg_type}")
        continue

    try:
        if msg_type == "what_if":
            send_poll(
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
    data["poll"]["question"],
    data["poll"]["options"]
            )
        else:
            send_telegram(
                TELEGRAM_TOKEN,
                TELEGRAM_CHAT_ID,
                message,
                msg_type
            )

        sent += 1
        print(f"✓ Message {index}/{len(messages)} sent")

    except Exception as e:
        failed += 1
        print(f"✗ Message {index} failed")
        print(e)

print("\n" + "=" * 50)

print("🍞 AI Bakery Finished")

print("=" * 50)

print(f"Messages Sent : {sent}")

print(f"Messages Failed : {failed}")

print(f"News Articles : {len(news_items)}")

print("=" * 50)
"""
