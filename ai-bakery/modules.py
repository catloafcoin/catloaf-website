# ==========================================================
# CatLoaf AI Bakery V3
# modules.py
# Utilities
# ==========================================================

import json
import os
import time
from html import escape

import requests

TELEGRAM_LIMIT = 4096
MESSAGE_LIMIT = 3900

REQUEST_TIMEOUT = 30
PHOTO_TIMEOUT = 90

MAX_RETRIES = 3

USER_AGENT = {
    "User-Agent": "Mozilla/5.0 CatLoaf AI Bakery"
}


# ==========================================================
# FILE HELPERS
# ==========================================================

def load_text(path):

    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:

        return f.read()


def save_text(path, text):

    with open(path, "w", encoding="utf-8") as f:

        f.write(text)


def load_json(path):

    if not os.path.exists(path):

        return {}

    try:

        with open(path, "r", encoding="utf-8") as f:

            return json.load(f)

    except json.JSONDecodeError as e:

        raise Exception(
            f"Invalid JSON in {path}\n{e}"
        )


# ==========================================================
# JSON VALIDATION
# ==========================================================

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

        data = json.loads(response)

    except Exception as e:

        raise Exception(
            f"Gemini returned invalid JSON\n\n{e}"
        )

    # ------------------------------------------------------
    # Required Objects
    # ------------------------------------------------------

    defaults = {

        "telegram": {},

        "art_image": {},

        "meme": {},

        "poll": {},

        "x_posts": [],

        "best_time": {}

    }

    for key, value in defaults.items():

        data.setdefault(key, value)

    tg = data["telegram"]

    tg.setdefault("persona", "CatLoaf")

    tg.setdefault("category", "Community")

    tg.setdefault("headline", "Today's Hot Loaf")

    tg.setdefault("opening", "")

    tg.setdefault("bullets", [])

    tg.setdefault("why", "")

    tg.setdefault("question", "")

    tg.setdefault("header_image", {})

    tg.setdefault("loaf_score", {})

    tg["header_image"].setdefault(

        "prompt",

        ""

    )

    score = tg["loaf_score"]

    score.setdefault("overall", 50)

    score.setdefault("market_impact", "Medium")

    score.setdefault("builder_interest", "Medium")

    score.setdefault("urgency", "Medium")

    art = data["art_image"]

    art.setdefault(

        "title",

        "CatLoaf Artwork"

    )

    art.setdefault(

        "caption",

        ""

    )

    art.setdefault(

        "prompt",

        "Cute CatLoaf artwork."

    )

    meme = data["meme"]

    meme.setdefault(

        "quote",

        ""

    )

    meme.setdefault(

        "cta",

        "Stay loafy."

    )

    poll = data["poll"]

    poll.setdefault(

        "question",

        "What are we baking today?"

    )

    poll.setdefault(

        "options",

        [

            "Builders",

            "Memecoins",

            "DeFi",

            "Validators"

        ]

    )

    while len(data["x_posts"]) < 3:

        data["x_posts"].append({

            "type": "fallback",

            "content": "🍞 Stay loafy."

        })

    best = data["best_time"]

    best.setdefault(

        "utc",

        "12:00 UTC"

    )

    best.setdefault(

        "reason",

        "Highest engagement"

    )

    best.setdefault(

        "audience",

        "Crypto Community"

    )

    return data

# ==========================================================
# TELEGRAM HELPERS
# ==========================================================

def telegram_safe(text):

    """
    Escapes HTML while preserving
    supported Telegram tags.
    """

    safe = escape(str(text))

    replacements = {

        "&lt;b&gt;": "<b>",
        "&lt;/b&gt;": "</b>",

        "&lt;i&gt;": "<i>",
        "&lt;/i&gt;": "</i>",

        "&lt;u&gt;": "<u>",
        "&lt;/u&gt;": "</u>",

        "&lt;code&gt;": "<code>",
        "&lt;/code&gt;": "</code>",

        "&lt;pre&gt;": "<pre>",
        "&lt;/pre&gt;": "</pre>"

    }

    for old, new in replacements.items():

        safe = safe.replace(old, new)

    return safe


# ==========================================================
# MESSAGE SPLITTER
# ==========================================================

def split_message(text, limit=MESSAGE_LIMIT):

    text = str(text)

    if len(text) <= limit:

        return [text]

    chunks = []

    while len(text) > limit:

        split = text.rfind(

            "\n",

            0,

            limit

        )

        if split == -1:

            split = text.rfind(

                " ",

                0,

                limit

            )

        if split == -1:

            split = limit

        chunks.append(

            text[:split]

        )

        text = text[split:].lstrip()

    if text:

        chunks.append(text)

    return chunks


# ==========================================================
# BUTTON HELPERS
# ==========================================================

def default_reply_markup(msg_type):

    if msg_type not in [

        "hot_loaf",

        "art",

        "cloaf"

    ]:

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

                custom.get(

                    "inline_keyboard",

                    []

                )

            )

        except Exception as e:

            print("=" * 60)
            print("BUTTON MERGE ERROR")
            print(e)
            print("=" * 60)

    if not rows:

        return None

    return json.dumps({

        "inline_keyboard": rows

    })


# ==========================================================
# TELEGRAM REQUEST LOGGER
# ==========================================================

def log_request(title, payload):

    print("=" * 60)

    print(title)

    print("=" * 60)

    for key, value in payload.items():

        if key == "text":

            preview = str(value)[:250]

            print(f"{key}: {preview}")

        else:

            print(f"{key}: {value}")

    print("=" * 60)

# ==========================================================
# TELEGRAM MESSAGE SENDER
# ==========================================================

def send_telegram(
    token,
    chat_id,
    text,
    msg_type,
    reply_markup=None
):

    if not text:

        print("⚠ Empty Telegram message.")

        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    keyboard = merge_reply_markup(
        reply_markup,
        msg_type
    )

    parts = split_message(text)

    total = len(parts)

    for index, part in enumerate(parts):

        payload = {

            "chat_id": chat_id,

            "text": telegram_safe(part),

            "parse_mode": "HTML",

            "disable_web_page_preview": True

        }

        # Only attach buttons to final chunk

        if keyboard and index == total - 1:

            payload["reply_markup"] = keyboard

        success = False

        for attempt in range(1, MAX_RETRIES + 1):

            try:

                log_request(

                    f"TELEGRAM MESSAGE ({attempt}/{MAX_RETRIES})",

                    payload

                )

                response = requests.post(

                    url,

                    data=payload,

                    timeout=REQUEST_TIMEOUT

                )

                print(

                    "Status:",

                    response.status_code

                )

                if response.status_code == 200:

                    success = True

                    break

                print(response.text)

            except Exception as e:

                print(

                    "Telegram Error:",

                    e

                )

            time.sleep(2)

        if not success:

            print("=" * 60)
            print("FAILED TO SEND MESSAGE")
            print("=" * 60)

            return False

        time.sleep(0.5)

    print("=" * 60)
    print("✓ TELEGRAM MESSAGE SENT")
    print("=" * 60)

    return True

# ==========================================================
# PHOTO SENDER
# ==========================================================

def send_photo(
    token,
    chat_id,
    photo_path,
    caption="",
    reply_markup=None,
    msg_type="art"
):

    if not photo_path:

        print("⚠ No image supplied.")

        return send_telegram(
            token,
            chat_id,
            caption,
            msg_type,
            reply_markup
        )

    keyboard = merge_reply_markup(
        reply_markup,
        msg_type
    )

    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    caption_text = caption
    followup = None

    if len(caption_text) > 1000:

        followup = caption_text

        caption_text = (
            "🍞 <b>Preview</b>\n\n"
            "Full post below ⬇️"
        )

    payload = {

        "chat_id": chat_id,

        "caption": telegram_safe(caption_text),

        "parse_mode": "HTML"

    }

    if keyboard:

        payload["reply_markup"] = keyboard

    temp_file = None

    success = False

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            print("=" * 60)
            print("PHOTO UPLOAD")
            print("=" * 60)
            print("Attempt :", attempt)
            print("Image   :", photo_path)

            # ----------------------------------------
            # Remote Image
            # ----------------------------------------

            if (
                isinstance(photo_path, str)
                and photo_path.startswith("http")
            ):

                temp_file = download_image(photo_path)

                if temp_file:

                    with open(temp_file, "rb") as photo:

                        response = requests.post(

                            url,

                            data=payload,

                            files={
                                "photo": photo
                            },

                            timeout=120

                        )

                else:

                    payload["photo"] = photo_path

                    response = requests.post(

                        url,

                        data=payload,

                        timeout=120

                    )

            # ----------------------------------------
            # Local Image
            # ----------------------------------------

            else:

                with open(photo_path, "rb") as photo:

                    response = requests.post(

                        url,

                        data=payload,

                        files={
                            "photo": photo
                        },

                        timeout=120

                    )

            print("Status :", response.status_code)

            print(response.text)

            if response.status_code == 200:

                success = True

                break

        except Exception as e:

            print("Photo upload failed:")

            print(e)

        time.sleep(3)

    # ----------------------------------------
    # Cleanup
    # ----------------------------------------

    if temp_file:

        try:

            if os.path.exists(temp_file):

                os.remove(temp_file)

        except Exception:

            pass

    # ----------------------------------------
    # Fallback
    # ----------------------------------------

    if not success:

        print("=" * 60)
        print("PHOTO FAILED")
        print("Sending text instead.")
        print("=" * 60)

        return send_telegram(

            token,

            chat_id,

            caption,

            msg_type,

            reply_markup

        )

    # ----------------------------------------
    # Long caption follow-up
    # ----------------------------------------

    if followup:

        send_telegram(

            token,

            chat_id,

            followup,

            msg_type,

            reply_markup

        )

    print("=" * 60)
    print("✓ PHOTO SENT")
    print("=" * 60)

    return True

# ==========================================================
# POLL SENDER
# ==========================================================

def send_poll(
    token,
    chat_id,
    question,
    options,
    reply_markup=None
):

    import json
    import requests
    import time

    print("=" * 70)
    print("🍞 POLL PUBLISH START")
    print("=" * 70)
    print("Chat ID :", chat_id)
    print("Question:", question)
    print("Options :", options)
    print("=" * 70)

    if not question:
        print("ERROR: Empty question")
        return False

    if not options or len(options) < 2:
        print("ERROR: Poll needs at least 2 options")
        return False

    url = f"https://api.telegram.org/bot{token}/sendPoll"

    payload = {
        "chat_id": chat_id,
        "question": question[:300],
        "options": json.dumps(options),
        
        "allows_multiple_answers": False
    }

    for attempt in range(1, 4):

        try:

            print(f"Attempt {attempt}")

            response = requests.post(
                url,
                data=payload,
                timeout=30
            )

            print("Status Code :", response.status_code)
            print("Response    :", response.text)

            if response.status_code == 200:

                print("=" * 70)
                print("✅ POLL SENT SUCCESSFULLY")
                print("=" * 70)

                return True

        except Exception as e:

            print("Exception:", e)

        time.sleep(2)

    print("=" * 70)
    print("❌ POLL FAILED")
    print("=" * 70)

    return False

# --------------------------------------------------
# RSS Image Downloader
# --------------------------------------------------

def download_image(url):

    if not url:
        return None

    print("=" * 60)
    print("DOWNLOADING RSS IMAGE")
    print(url)
    print("=" * 60)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/131 Safari/537.36"
        )
    }

    for attempt in range(1, 4):

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=90,
                stream=True
            )

            if response.status_code != 200:

                print(
                    f"Attempt {attempt}:",
                    response.status_code
                )

                time.sleep(3)

                continue

            content_type = response.headers.get(
                "Content-Type",
                ""
            ).lower()

            extension = ".jpg"

            if "png" in content_type:
                extension = ".png"

            elif "webp" in content_type:
                extension = ".webp"

            filename = (
                f"rss_{int(time.time())}"
                f"{extension}"
            )

            with open(filename, "wb") as f:

                for chunk in response.iter_content(8192):

                    if chunk:

                        f.write(chunk)

            if os.path.getsize(filename) < 5000:

                print("Downloaded image too small.")

                os.remove(filename)

                time.sleep(3)

                continue

            print("✓ RSS image downloaded")
            print(filename)

            return filename

        except Exception as e:

            print(
                f"Attempt {attempt} failed:"
            )

            print(e)

            time.sleep(3)

    print("⚠ RSS image download failed.")

    return None
