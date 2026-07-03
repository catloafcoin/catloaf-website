import json
import time
import requests
from html import escape

TELEGRAM_LIMIT = 4096


# --------------------------------------------------
# File Helpers
# --------------------------------------------------

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

    try:

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        return {}

    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in {path}: {e}")


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


# --------------------------------------------------
# Telegram Helpers
# --------------------------------------------------

def telegram_safe(text):

    safe = escape(str(text))

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

    text = str(text)

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


# --------------------------------------------------
# Button Helpers
# --------------------------------------------------

def default_reply_markup(msg_type):

    if msg_type not in ["hot_loaf", "art", "cloaf"]:
        return []

    return [
        [
            {
                "text": "🐦 Follow X",
                "url": "https://x.com/CatLoafCoin"
            },
            {
                "text": "📢 Telegram",
                "url": "https://t.me/CatLoafCoin"
            }
        ]
    ]


def merge_reply_markup(reply_markup, msg_type):

    rows = default_reply_markup(msg_type)

    if reply_markup:

        try:

            custom = json.loads(reply_markup)

            rows.extend(
                custom.get("inline_keyboard", [])
            )

        except Exception as e:

            print("Button merge failed:", e)

    if not rows:
        return None

    return json.dumps({
        "inline_keyboard": rows
    })

def send_telegram(token, chat_id, text, msg_type, reply_markup=None):

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    merged_markup = merge_reply_markup(
        reply_markup,
        msg_type
    )

    parts = split_message(text)

    for index, part in enumerate(parts):

        success = False

        for attempt in range(3):

            payload = {
                "chat_id": chat_id,
                "text": telegram_safe(part),
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }

            # Only attach buttons to the last message
            if merged_markup and index == len(parts) - 1:
                payload["reply_markup"] = merged_markup

            print("=" * 60)
            print("SENDING TELEGRAM MESSAGE")
            print("Attempt:", attempt + 1)
            print("Chat ID:", chat_id)
            print("Type:", msg_type)
            print("Payload:")
            print(payload)
            print("=" * 60)

            try:

                r = requests.post(
                    url,
                    data=payload,
                    timeout=20
                )

                print("=" * 60)
                print("TELEGRAM RESPONSE")
                print("Status:", r.status_code)
                print("Response:", r.text)
                print("=" * 60)

                if r.status_code == 200:
                    success = True
                    break

            except Exception as e:

                print(f"Telegram Error: {e}")

            time.sleep(2)

        if not success:
            print("⚠ Telegram send failed after 3 attempts.")

        time.sleep(1)

# --------------------------------------------------
# Photo Sender
# --------------------------------------------------

def send_photo(
    token,
    chat_id,
    photo_path,
    caption="",
    reply_markup=None,
    msg_type="art"
):

    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    merged_markup = merge_reply_markup(
    reply_markup,
    msg_type
)

    with open(photo_path, "rb") as photo:

        payload = {
            "chat_id": chat_id,
            "caption": telegram_safe(caption),
            "parse_mode": "HTML"
        }

        if merged_markup:
            payload["reply_markup"] = merged_markup

        r = requests.post(
            url,
            data=payload,
            files={
                "photo": photo
            },
            timeout=60
        )

    print("=" * 60)
    print("PHOTO RESPONSE")
    print(r.status_code)
    print(r.text)
    print("=" * 60)

    if r.status_code != 200:
        raise Exception(r.text)


# --------------------------------------------------
# Poll Sender
# --------------------------------------------------

def send_poll(
    token,
    chat_id,
    question,
    options,
    reply_markup=None
):

    if not question or not options:
        return

    url = f"https://api.telegram.org/bot{token}/sendPoll"

    payload = {
        "chat_id": chat_id,
        "question": question,
        "options": json.dumps(options),
        "is_anonymous": False,
        "allows_multiple_answers": False
    }

    merged_markup = merge_reply_markup(
        reply_markup,
        "poll"
    )

    if merged_markup:
        payload["reply_markup"] = merged_markup

    r = requests.post(
        url,
        data=payload,
        timeout=20
    )

    print("=" * 60)
    print("POLL RESPONSE")
    print(r.status_code)
    print(r.text)
    print("=" * 60)

    if r.status_code != 200:
        raise Exception(r.text)