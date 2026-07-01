import google.generativeai as genai
import requests
import os
import json
import modules
from rss_reader import get_latest_news
from html import escape

print("Starting AI Bakery...")

news = get_latest_news()

seen = set()
news_text = ""

for article in news:
    title = article["title"].strip()

    if title.lower() in seen:
        continue

    seen.add(title.lower())
    news_text += f"• {title}\n"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

with open("config.json", "r") as f:
    config = json.load(f)

with open("brand.txt", "r", encoding="utf-8") as f:
    brand_guide = f.read()

try:
    with open("history.txt", "r", encoding="utf-8") as f:
        history = f.read()
except FileNotFoundError:
    history = ""

prompt = f"""
{brand_guide}
Previous generated content:
{history}

Latest Solana News:
{news_text}

Use the news above to create a DAILY SOLANA ALPHA section.

Only use information from the news above.
If no news fits a category, leave it out.
Never invent facts.

You are CatLoaf's official AI Marketing Director.

Brand personality:

- Wholesome
- Witty
- Internet-native
- Community first
- Cat + Bread + Solana culture

Generate the following using these EXACT headings.

===SECTION:DAILY_ALPHA===

Include:

🔥 Top Solana headline

🚀 Biggest ecosystem update

🪙 Trending memecoin mention (if available)

🧠 One sentence explaining why today's news matters.

Keep it concise.

===SECTION:X_POST===

Create THREE different X posts.

① VIRAL
② FUNNY
③ EDUCATIONAL

Each post:

• Maximum 280 characters
• Natural
• Human
• Internet-native
• One call to action
• Maximum 3 hashtags

Never sound like AI.

Use CatLoaf personality.

Leave one blank line between each post.


===SECTION:TELEGRAM_POST===

Write a PREMIUM Telegram announcement.

Formatting:

🍞🐱 CATLOAF DAILY BAKERY
━━━━━━━━━━━━━━━━━━━━━━

☀️ GM Bakers!

Write ONE warm and exciting opening sentence.

Leave ONE blank line.

🔥 TODAY'S FRESH ALPHA

Summarize today's biggest Solana news in 2-4 short bullet points.

Leave ONE blank line.

🧠 WHY IT MATTERS

Explain why the news is important in 2 short sentences.

Leave ONE blank line.

💬 COMMUNITY QUESTION

Ask ONE engaging question.

Leave ONE blank line.

━━━━━━━━━━━━━━━━━━━━━━
🍞 Stay Cozy. Stay Curious.
🐱 @CatLoafCoin

Rules:
• Maximum 220 words.
• Never create long paragraphs.
• Maximum 2 sentences per paragraph.
• Use emojis only as section headings.
• Make it look premium and highly readable.

===SECTION:MEME_IDEA===

Create a meme using this format.

😂 TEMPLATE

Popular meme format

🎬 SCENE

Describe exactly what happens.

💬 CAPTION

Funny caption.

🤣 WHY IT WORKS

One sentence.

Keep it viral and easy to understand.


===SECTION:IMAGE_PROMPT===

Create an AI image prompt using this format.

🎨 STYLE

📸 CAMERA

💡 LIGHTING

🌅 BACKGROUND

🐱 SUBJECT

🎨 COLOR PALETTE

😊 MOOD

✨ DETAILS

Ultra detailed
8K
Photorealistic
Professional composition
Trending on X

===SECTION:ENGAGEMENT===

Generate THREE community questions.

① Funny

② Crypto

③ Cozy

Maximum one sentence each.

Questions should encourage replies.


===SECTION:BEST_TIME===

Recommend ONE posting time.

Format:

🕒 BEST TIME

Time (UTC)

🌍 WHY

One short explanation.

🎯 AUDIENCE

Who will be online.

==========================
GLOBAL FORMATTING
==========================

Every section must look like a premium Telegram channel.

Always use:

━━━━━━━━━━━━━━━━━━━━━━

between major topics.

Leave ONE blank line after every heading.

Leave ONE blank line before every bullet list.

Never write walls of text.

Maximum 3 lines per paragraph.

Use emojis only for headings.

Write like a professional crypto community manager.

Write naturally.

Never sound robotic.

Never repeat previous wording.

Never use generic ChatGPT phrases.

Every output should feel handcrafted.

Use cozy bakery branding whenever appropriate.

Readers should immediately recognize the CatLoaf identity.

The goal is to make every message beautiful, premium, easy to scan, and highly shareable.

OUTPUT STYLE

Every section should look like it belongs in a premium crypto Telegram channel.

Return ONLY Telegram-supported HTML.

Allowed tags:
<b>
<i>
<code>

Do NOT use:
<h1>
<h2>
<h3>
<p>
<div>
<span>
<br>
<center>
<ul>
<li>

Never generate any HTML tags except <b>, <i>, and <code>.

Output must be accepted by Telegram Bot API using parse_mode=HTML.

Never overuse formatting.

<i>Emphasis only when useful</i>

Every message should be:

• Beautiful

• Easy to skim

• Premium

• Human

• Cozy

• Shareable

Write like the best crypto social media manager.

Every post should be worth forwarding.

QUALITY CHECK

Before finishing, verify:

✅ Beautiful formatting
✅ Excellent spacing
✅ Easy to skim
✅ Premium appearance
✅ Human writing
✅ No repeated ideas
✅ No walls of text
✅ Fits Telegram perfectly

If any check fails, rewrite the section before responding.

Rules:
- Never mention guaranteed profits.
- Never predict price.
- Never repeat previous ideas.
- Make every run unique.
- Keep everything positive and community-driven.

"""

generation_config = {
    "temperature": 1.15,
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

message = response.text

print(message)

try:
    with open("history.txt", "r", encoding="utf-8") as f:
        history_entries = f.read().split("\n\n---ENTRY---\n\n")
except FileNotFoundError:
    history_entries = []

summary = []

for section in message.split("===SECTION:"):
    section = section.strip()
    if not section:
        continue

    lines = section.splitlines()

    # Keep only the first 3 non-empty lines from each section
    kept = [line for line in lines if line.strip()][:3]

    summary.append("\n".join(kept))

history_entries.append("\n\n".join(summary))

# Keep only the latest 10 generations
history_entries = history_entries[-10:]

with open("history.txt", "w", encoding="utf-8") as f:
    f.write("\n\n---ENTRY---\n\n".join(history_entries))

sections = message.split("===SECTION:")

sections = message.split("===SECTION:")

for section in sections:
    section = section.strip()

    if not section:
        continue

    lines = section.splitlines()

    if len(lines) > 1:
        section = "\n".join(lines[1:]).strip()

    safe_text = escape(section)

    safe_text = (
        safe_text
        .replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
        .replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
        .replace("&lt;code&gt;", "<code>").replace("&lt;/code&gt;", "</code>")
    )

    r = requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage",
        data={
            "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
            "text": safe_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        },
        timeout=20
    )

    print(f"Telegram Status: {r.status_code}")
    print(r.text)
