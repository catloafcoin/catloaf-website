import google.generativeai as genai
import requests
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

prompt = """
You are the marketing manager for CatLoaf, a Solana meme coin.

Generate:

1. One viral X post
2. One Telegram post
3. One meme idea
4. One image prompt
5. One engagement question

Keep the tone fun, wholesome, witty and community-driven.
Avoid making false promises or price predictions.
"""

response = model.generate_content(prompt)

message = response.text

requests.post(
    f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage",
    data={
        "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "text": message
    }
)
