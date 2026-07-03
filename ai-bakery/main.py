from scheduler import add_to_queue, save_daily, calculate_score
from image_generator import generate_image
import os
import json
import uuid
import google.generativeai as genai
from rss_reader import get_latest_news, score_articles
from poster import process_queue
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
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")
GEMINI_API_KEY_3 = os.getenv("GEMINI_API_KEY_3")
GEMINI_API_KEY_4 = os.getenv("GEMINI_API_KEY_4")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not GEMINI_API_KEY:
    raise Exception("Missing GEMINI_API_KEY")

if not TELEGRAM_TOKEN:
    raise Exception("Missing TELEGRAM_BOT_TOKEN")

if not TELEGRAM_CHAT_ID:
    raise Exception("Missing TELEGRAM_CHAT_ID")

API_KEYS = [
    GEMINI_API_KEY,
    GEMINI_API_KEY_2,
    GEMINI_API_KEY_3,
    GEMINI_API_KEY_4
]

print("✓ Configuration Loaded")
RUN_ID = uuid.uuid4().hex[:8]

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

articles = score_articles(get_latest_news())

print("Top News Scores:")

for article in articles[:5]:
    print(article["score"], "-", article["title"])

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
# Detect if today's news is fresh
# --------------------------------------------------

highest_score = max((a["score"] for a in articles), default=0)

print(f"Highest News Score: {highest_score}")

hot_news_found = highest_score >= 25

print(f"✓ Hot News Found: {hot_news_found}")

# --------------------------------------------------
# Build Prompt
# --------------------------------------------------

prompt = f"""
{brand}

{prompt_template}
"""

if hot_news_found:

    prompt = (
        prompt
        .replace("{news}", news_text)
        .replace("{history}", history)
    )

else:

    prompt = (
        prompt
        .replace("{news}", "No major Solana news today.")
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
    "response_mime_type": "application/json"
}

response = None
last_error = None

for api_key in API_KEYS:

    if not api_key:
        continue

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        print("✓ Gemini request successful")
        break

    except Exception as e:

        print(f"API key failed: {e}")
        last_error = e

if response is None:
    raise last_error

if not hasattr(response, "text") or not response.text:
    raise Exception("Gemini returned an empty response.")

print("✓ Gemini Response Received")

print("=" * 50)
print(response.text)
print("=" * 50)
data = validate_json(response.text)

required_keys = [
    "telegram",
    "art_image",
    "meme",
    "poll",
    "x_posts",
    "best_time"
]

for key in required_keys:
    if key not in data:
        raise Exception(f"Gemini response missing '{key}'.")

print("✓ JSON Validated")

score = calculate_score(data)

print(f"✓ Content Score: {score}/100")

if score >= 80:
    save_daily(data)
    print("✓ Daily content saved")
else:
    print("✗ Content score too low. Skipping.")

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

persona = tg.get("persona", "CatLoaf")

category = tg.get("category", "Community")

headline = tg.get("headline", "TODAY'S HOT LOAF")

source = tg.get("source", {})

source_title = source.get("title", "")

source_url = source.get("url", "")

loaf_score = tg.get("loaf_score", {})

overall = loaf_score.get("overall", "-")

market = loaf_score.get("market_impact", "-")

builder = loaf_score.get("builder_interest", "-")

urgency = loaf_score.get("urgency", "-")

telegram_message = f"""
🔥 <b>{headline}</b>

{divider()}

🍞 <i>Fresh from today's oven...</i>

{tg.get("opening", "")}

🔥 <b>Fresh Alpha</b>
"""

for bullet in tg.get("bullets", []):
    telegram_message += f"\n• {bullet}"

telegram_message += "\n\n🧈 <b>Why It Matters</b>\n\n"
telegram_message += tg.get("why", "")

telegram_message += "\n\n📊 <b>Loaf Score</b>\n"

if str(overall).isdigit():
    telegram_message += f"\n🍞 Overall: {overall}/100"
else:
    telegram_message += f"\n🍞 Overall: {overall}"

telegram_message += f"""

📈 Market Impact: {market}

🏗 Builder Interest: {builder}

⚡ Urgency: {urgency}

🥖 <b>Hot Take</b>

{tg.get("question", "")}

{divider()}
🐱 @CatLoafCoin
"""

messages.append(telegram_message.strip())
message_types.append("hot_loaf")

hot_loaf = {
    "id": f"hot_loaf_{RUN_ID}",
    "type": "hot_loaf",
    "text": telegram_message.strip(),
    "image": None,
    "header_image": None,
    "source_title": source_title,
    "source_url": source_url,
    "persona": persona,
    "category": category
}

# --------------------------------------------------
# IMAGES
# --------------------------------------------------

meme = data.get("meme", {})
art = data.get("art_image", {})
header = tg.get("header_image", {})

if not art:
    raise Exception("Missing art_image from Gemini.")

if not header:
    raise Exception("Missing header_image from Gemini.")

if not meme:
    raise Exception("Missing meme from Gemini.")

print("=" * 50)
print("ART IMAGE JSON")
print(json.dumps(art, indent=2, ensure_ascii=False))
print("=" * 50)

print("=" * 50)
print("HEADER IMAGE JSON")
print(json.dumps(header, indent=2, ensure_ascii=False))
print("=" * 50)

# Generate header image
header_image_path = generate_image(header)

# Generate art image
image_path = generate_image(art)

print("✓ Header Image Generated")
print("✓ Art Image Generated")

meme_message = f"""
🎨 <b>{art.get("title", "Art of the Day")}</b>

{divider()}

<i>"{meme.get("quote", "")}"</i>

{art.get("caption", "")}

🥖 {meme.get("cta", "")}
"""

messages.append(meme_message.strip())
message_types.append("art")

art_post = {
    "id": f"art_{RUN_ID}",
    "type": "art",
    "title": art.get("title", ""),
    "caption": art.get("caption", ""),
    "quote": meme.get("quote", ""),
    "cta": meme.get("cta", ""),
    "image": image_path
}

# Update Hot Loaf to use generated header image
hot_loaf["image"] = header_image_path

# --------------------------------------------------
# POLL
# --------------------------------------------------

messages.append(data["poll"]["question"])
message_types.append("what_if")

poll_post = {
    "id": f"poll_{RUN_ID}",
    "type": "what_if",
    "text": data["poll"]["question"],
    "image": None,
    "question": data["poll"]["question"],
    "options": data["poll"]["options"]
}
x_posts = data.get("x_posts", [])

while len(x_posts) < 3:
    x_posts.append({
        "type": "fallback",
        "content": "🍞 Stay loafy with $CLOAF!"
    })

x_viral = {
    "id": f"x_viral_{RUN_ID}",
    "type": "x_viral",
    "text": x_posts[0]["content"],
    "image": None
}

x_funny = {
    "id": f"x_funny_{RUN_ID}",
    "type": "x_funny",
    "text": x_posts[1]["content"],
    "image": None
}

x_educational = {
    "id": f"x_educational_{RUN_ID}",
    "type": "x_educational",
    "text": x_posts[2]["content"],
    "image": None
}

# Queue AI Art
add_to_queue(art_post)

# Queue Hot Loaf
if hot_news_found:
    add_to_queue(hot_loaf)
    print("✓ Fresh Hot Loaf queued")
else:
    print("⚠ No major news today. Skipping Hot Loaf.")

# Queue Poll
add_to_queue(poll_post)

# Queue X Posts
add_to_queue(x_viral)
add_to_queue(x_funny)
add_to_queue(x_educational)

print("✓ Queue Updated")
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

print("Starting poster...")
process_queue()
print("Poster finished.")