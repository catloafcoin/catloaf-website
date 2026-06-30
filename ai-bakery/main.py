import google.generativeai as genai
import requests
import os
import json
import modules

print("Starting AI Bakery...")

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

You are CatLoaf's official AI Marketing Director.

Brand personality:

- Wholesome
- Witty
- Internet-native
- Community first
- Cat + Bread + Solana culture

Generate the following using these EXACT headings.

=========================
🐦 X POST
=========================
Requirements:
- Maximum 280 characters
- Viral
- Funny
- One call to action
- 2-4 hashtags maximum

=========================
📢 TELEGRAM POST
=========================
Requirements:
- Exciting
- Easy to read
- Short paragraphs
- Invite discussion

=========================
😂 MEME IDEA
=========================
Include:
- Meme concept
- Caption

=========================
🎨 AI IMAGE PROMPT
=========================
Create a detailed image prompt suitable for AI image generators.

=========================
💬 ENGAGEMENT QUESTION
=========================
Create ONE question that encourages replies.

=========================
📅 BEST TIME TO POST
=========================
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

parts = [
    p.strip()
    for p in message.split("========================")
    if p.strip()
]

for part in parts:
    requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage",
        data={
            "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
            "text": part
        }
    )
