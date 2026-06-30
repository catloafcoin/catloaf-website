import google.generativeai as genai
import requests
import os
import json
import modules
from rss_reader import get_latest_news

print("Starting AI Bakery...")

news = get_latest_news()

news_text = ""

for article in news:
    news_text += f"- {article['title']}\n"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

with open("config.json", "r") as f:
    config = json.load(f)

with open("brand.txt", "r", encoding="utf-8") as f:
    brand_guide = f.read()

with open("history.txt", "r", encoding="utf-8") as f:
    history = f.read()

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
Requirements:
- Maximum 280 characters
- Viral
- Funny
- One call to action
- 2-4 hashtags maximum

===SECTION:TELEGRAM_POST===
Requirements:
- Exciting
- Easy to read
- Short paragraphs
- Invite discussion

===SECTION:MEME_IDEA===
Include:
- Meme concept
- Caption

===SECTION:IMAGE_PROMPT===
Create a detailed image prompt suitable for AI image generators.
===SECTION:ENGAGEMENT===
Create ONE question that encourages replies.

===SECTION:BEST_TIME===
Suggest the best UTC posting time and explain why in one sentence.

Rules:
- Never mention guaranteed profits.
- Never predict price.
- Never repeat previous ideas.
- Make every run unique.
- Keep everything positive and community-driven.
"""

response = model.generate_content(prompt)

message = response.text

print(message)

sections = message.split("===SECTION:")

for section in sections:
    section = section.strip()

    if not section:
        continue

    requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage",
        data={
            "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
            "text": section.strip()
        }
    )
