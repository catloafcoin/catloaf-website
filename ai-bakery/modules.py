import json
import os
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

        raise Exception(
            f"Invalid JSON in {path}: {e}"
        )


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
            f"Invalid JSON from Gemini:\n{e}"
        )

    # --------------------------------------------------
    # Required top-level objects
    # --------------------------------------------------

    data.setdefault("telegram", {})
    data.setdefault("art_image", {})
    data.setdefault("meme", {})
    data.setdefault("poll", {})
    data.setdefault("x_posts", [])
    data.setdefault("best_time", {})

    # --------------------------------------------------
    # Telegram defaults
    # --------------------------------------------------

    telegram = data["telegram"]

    telegram.setdefault("persona", "CatLoaf")
    telegram.setdefault("category", "Community")
    telegram.setdefault("headline", "Today's Hot Loaf")
    telegram.setdefault("opening", "")
    telegram.setdefault("bullets", [])
    telegram.setdefault("why", "")
    telegram.setdefault("question", "")
    telegram.setdefault("header_image", {})
    telegram.setdefault("loaf_score", {})

    telegram["header_image"].setdefault(
        "prompt",
        ""
    )

    loaf = telegram["loaf_score"]

    loaf.setdefault("overall", 50)
    loaf.setdefault("market_impact", "Medium")
    loaf.setdefault("builder_interest", "Medium")
    loaf.setdefault("urgency", "Medium")

    # --------------------------------------------------
    # Art defaults
    # --------------------------------------------------

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
        "Cute CatLoaf digital illustration."
    )

    # --------------------------------------------------
    # Meme defaults
    # --------------------------------------------------

    meme = data["meme"]

    meme.setdefault("quote", "")
    meme.setdefault("cta", "Stay loafy.")

    # --------------------------------------------------
    # Poll defaults
    # --------------------------------------------------

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

    # --------------------------------------------------
    # X post defaults
    # --------------------------------------------------

    while len(data["x_posts"]) < 3:

        data["x_posts"].append({

            "type": "fallback",

            "content": "🍞 Stay loafy."

        })

    # --------------------------------------------------
    # Best time defaults
    # --------------------------------------------------

    best = data["best_time"]

    best.setdefault(
        "utc",
        "12:00 UTC"
    )

    best.setdefault(
        "reason",
        "General engagement"
    )

    best.setdefault(
        "audience",
        "Crypto Community"
    )

    return data


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

        split = text.rfind(
            "\n",
            0,
            limit
        )

        if split == -1:
            split = limit

        chunks.append(
            text[:split]
        )

        text = text[split:].lstrip()

    chunks.append(text)

    return chunks

# --------------------------------------------------
# Buttons
# --------------------------------------------------

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

            print("Button merge failed:", e)

    if not rows:
        return None

    return json.dumps({
        "inline_keyboard": rows
    })


# --------------------------------------------------
# Telegram Text
# --------------------------------------------------

def send_telegram(
    token,
    chat_id,
    text,
    msg_type,
    reply_markup=None
):

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

            # Buttons only on final chunk
            if (
                merged_markup
                and index == len(parts) - 1
            ):
                payload["reply_markup"] = merged_markup

            try:

                response = requests.post(
                    url,
                    data=payload,
                    timeout=30
                )

                print("=" * 60)
                print("SEND MESSAGE")
                print("Attempt :", attempt + 1)
                print("Chat ID :", chat_id)
                print("Type    :", msg_type)
                print("Status  :", response.status_code)
                print(response.text)
                print("=" * 60)

                if response.status_code == 200:
                    success = True
                    break

            except Exception as e:

                print("Telegram Error:", e)

            time.sleep(2)

        if not success:

            print("⚠ Telegram message failed after 3 attempts.")

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

    if not photo_path:

        print("⚠ No image supplied. Sending text instead.")

        send_telegram(
            token,
            chat_id,
            caption,
            msg_type,
            reply_markup
        )

        return

    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    merged_markup = merge_reply_markup(
        reply_markup,
        msg_type
    )

    caption_text = caption
    followup_text = None

    if len(caption_text) > 1000:

        followup_text = caption_text

        caption_text = (
            "🍞 <b>Preview</b>\n\n"
            "Full post below ⬇️"
        )

    payload = {
        "chat_id": chat_id,
        "caption": telegram_safe(caption_text),
        "parse_mode": "HTML"
    }

    if merged_markup:
        payload["reply_markup"] = merged_markup

    success = False
    local_image = None

    for attempt in range(3):

        try:

            print("=" * 60)
            print("PHOTO SEND")
            print("Attempt :", attempt + 1)
            print("Image   :", photo_path)
            print("=" * 60)

            # -----------------------------------
            # RSS Image URL
            # -----------------------------------

            if (
                isinstance(photo_path, str)
                and (
                    photo_path.startswith("http://")
                    or photo_path.startswith("https://")
                )
            ):

                local_image = download_image(photo_path)

                if local_image:

                    with open(local_image, "rb") as photo:

                        response = requests.post(
                            url,
                            data=payload,
                            files={
                                "photo": photo
                            },
                            timeout=90
                        )

                else:

                    payload["photo"] = photo_path

                    response = requests.post(
                        url,
                        data=payload,
                        timeout=90
                    )

            # -----------------------------------
            # Local AI Image
            # -----------------------------------

            else:

                with open(photo_path, "rb") as photo:

                    response = requests.post(
                        url,
                        data=payload,
                        files={
                            "photo": photo
                        },
                        timeout=90
                    )

            print("=" * 60)
            print("PHOTO RESPONSE")
            print("Status :", response.status_code)
            print(response.text)
            print("=" * 60)

            if response.status_code == 200:

                if local_image:

                    import os

                    try:

                        if os.path.exists(local_image):
                            os.remove(local_image)

                    except Exception:
                        pass

                success = True
                break

        except Exception as e:

            print("Photo Error:", e)

        time.sleep(3)

    if not success:

        print("⚠ Photo upload failed.")
        print("Sending text instead...")

        send_telegram(
            token,
            chat_id,
            caption,
            msg_type,
            reply_markup
        )

        return

    if followup_text:

        send_telegram(
            token,
            chat_id,
            followup_text,
            msg_type,
            reply_markup
        )

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

    if not question:

        print("⚠ Empty poll question.")
        return

    if not options or len(options) < 2:

        print("⚠ Invalid poll options.")
        return

    url = f"https://api.telegram.org/bot{token}/sendPoll"

    payload = {
        "chat_id": chat_id,
        "question": question[:300],
        "options": json.dumps(options),
        "is_anonymous": False,
        "allows_multiple_answers": False
    }

    for attempt in range(3):

        try:

            print("=" * 60)
            print("SENDING POLL")
            print("Attempt :", attempt + 1)
            print("Question:", question)
            print("Options :", options)
            print("=" * 60)

            response = requests.post(
                url,
                data=payload,
                timeout=30
            )

            print("=" * 60)
            print("POLL RESPONSE")
            print("Status :", response.status_code)
            print(response.text)
            print("=" * 60)

            if response.status_code == 200:

                return True

        except Exception as e:

            print("Poll Error:", e)

        time.sleep(2)

    print("⚠ Poll failed after 3 attempts.")

    send_telegram(
        token,
        chat_id,
        f"<b>Poll could not be published.</b>\n\n{question}",
        "poll"
    )

    return False


# --------------------------------------------------
# RSS Image Downloader
# --------------------------------------------------

def download_image(url):

    try:

        print("=" * 60)
        print("DOWNLOADING RSS IMAGE")
        print(url)
        print("=" * 60)

        response = requests.get(
            url,
            timeout=60,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if response.status_code != 200:

            print(
                "Download failed:",
                response.status_code
            )

            return None

        extension = ".jpg"

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "png" in content_type:
            extension = ".png"

        filename = (
            f"rss_{int(time.time())}"
            f"{extension}"
        )

        with open(filename, "wb") as f:

            f.write(response.content)

        print("✓ RSS image downloaded")

        return filename

    except Exception as e:

        print("RSS download failed:", e)

        return None