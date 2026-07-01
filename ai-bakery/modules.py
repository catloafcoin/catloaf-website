import json
import time
import requests
from html import escape

TELEGRAM_LIMIT = 4096


def load_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def save_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_json(response):
    try:
        return json.loads(response)
    except Exception as e:
        raise Exception(f"Invalid JSON from Gemini:\n{e}")


def telegram_safe(text):

    safe = escape(text)

    safe = (
        safe
        .replace("&lt;b&gt;", "<b>")
        .replace("&lt;/b&gt;", "</b>")
        .replace("&lt;i&gt;", "<i>")
        .replace("&lt;/i&gt;", "</i>")
        .replace("&lt;code&gt;", "<code>")
        .replace("&lt;/code&gt;", "</code>")
    )

    return safe


def split_message(text, limit=3900):

    if len(text) <= limit:
        return [text]

    chunks = []

    while len(text) > limit:

        split = text.rfind("\n", 0, limit)

        if split == -1:
            split = limit

        chunks.append(text[:split])

        text = text[split:].lstrip()

    chunks.append(text)

    return chunks


def send_telegram(token, chat_id, text):

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    parts = split_message(text)

    for part in parts:

        success = False

        for _ in range(3):

            r = requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "text": telegram_safe(part),
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                },
                timeout=20
            )

            if r.status_code == 200:
                success = True
                break

            time.sleep(2)

        print(r.status_code)
        print(r.text)

        if not success:
            print("Telegram send failed.")

        time.sleep(1)
