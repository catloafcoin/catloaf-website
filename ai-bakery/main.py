import google.generativeai as genai
import requests
import os

print("Starting AI Bakery...")

api_key = os.getenv("GEMINI_API_KEY")
print("API key found:", bool(api_key))

genai.configure(api_key=api_key)

print("Connecting to Gemini...")

model = genai.GenerativeModel("gemini-2.5-flash")

prompt = """
Write one fun CatLoaf X post in under 280 characters.
"""

response = model.generate_content(prompt)

print("Gemini replied.")

message = response.text

print(message)

bot = os.getenv("TELEGRAM_BOT_TOKEN")
chat = os.getenv("TELEGRAM_CHAT_ID")

print("Sending to Telegram...")

r = requests.post(
    f"https://api.telegram.org/bot{bot}/sendMessage",
    data={
        "chat_id": chat,
        "text": message
    }
)

print("Telegram status:", r.status_code)
print("Telegram response:", r.text)
