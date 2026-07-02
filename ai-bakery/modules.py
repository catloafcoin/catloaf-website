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

    response = response.strip()

    if response.startswith("```json"):
        response = response[7:]

    if response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]

    response = response.strip()

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


def send_telegram(token, chat_id, text, msg_type):

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    parts = split_message(text)

    for part in parts:

        success = False

        for _ in range(3):

            reply_markup = None

            if msg_type in ["hot_loaf", "art", "cloaf"]:

                reply_markup = json.dumps({
                    "inline_keyboard": [
                        [
                            {
                                "text": "🐦 Follow X",
                                "url": "https://x.com/CatLoafCoin"
                            },
                            {
                                "text": "📢 Telegram",
                                "url": "https://t.me/CatLoafCoin"
                            }
                        ],
                        [
                            {
                                "text": "📤 Share",
                                "switch_inline_query": "Join CatLoafCoin 🥖🐱 https://t.me/CatLoafCoin"
                            }
                        ]
                    ]
                })

            payload = {
                "chat_id": chat_id,
                "text": telegram_safe(part),
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }

            if reply_markup:
                payload["reply_markup"] = reply_markup

            r = requests.post(
                url,
                data=payload,
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

def send_photo(token, chat_id, photo_path, caption=""):

    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    reply_markup = json.dumps({
        "inline_keyboard": [
            [
                {
                    "text": "🐦 Follow X",
                    "url": "https://x.com/CatLoafCoin"
                },
                {
                    "text": "📢 Telegram",
                    "url": "https://t.me/CatLoafCoin"
                }
            ],
            [
                {
                    "text": "📤 Share",
                    "switch_inline_query": "Join CatLoafCoin 🥖🐱 https://t.me/CatLoafCoin"
                }
            ]
        ]
    })

    with open(photo_path, "rb") as photo:

        r = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "caption": telegram_safe(caption),
                "parse_mode": "HTML",
                "reply_markup": reply_markup
            },
            files={
                "photo": photo
            },
            timeout=60
        )

    print(r.status_code)
    print(r.text)

    if r.status_code != 200:
        raise Exception(r.text)

def send_poll(token, chat_id, question, options):

    if not question or not options:
        return
    
    url = f"https://api.telegram.org/bot{token}/sendPoll"

    r = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "question": question,
            "options": json.dumps(options),
            "is_anonymous": False,
            "allows_multiple_answers": False
        },
        timeout=20
    )

    if r.status_code != 200:
        raise Exception(r.text)
