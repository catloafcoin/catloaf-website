import google.generativeai as genai
import requests
import os

print("Starting AI Bakery...")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

prompt = """
You are the official AI marketing manager for CatLoaf, a wholesome Solana meme coin.

Generate the following:

🐦 X POST
- Short
- Viral
- Funny
- Under 280 characters

📢 TELEGRAM POST
- 2-4 paragraphs
- Community focused
- Fun and engaging

😂 MEME IDEA
- One unique meme concept

🎨 AI IMAGE PROMPT
- Detailed prompt for AI image generation

💬 ENGAGEMENT QUESTION
- One question to encourage replies

Rules:
- Never mention price predictions.
- Never promise profits.
- Keep the tone wholesome, funny and community-driven.
- Every response should be different.
"""

response = model.generate_content(prompt)

message = response.text

print(message)

requests.post(
    f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage",
    data={
        "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "text": message
    }
)
