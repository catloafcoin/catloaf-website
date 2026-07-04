import os
import json

from modules import (
    send_telegram,
    send_photo,
    send_poll
)

PUBLIC_CHAT_ID = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# --------------------------------------------------
# Publish Router
# --------------------------------------------------

def publish(item, destination="telegram"):

    print("=" * 60)
    print("PUBLISH REQUEST")
    print("=" * 60)
    print("Destination :", destination)
    print("Type        :", item.get("type"))
    print("Image       :", item.get("image"))
    print("Source      :", item.get("source_title", ""))
    print("=" * 60)

    handlers = {

        "telegram": publish_to_telegram,

        "x": publish_to_x,

        "both": publish_to_both

    }

    handler = handlers.get(destination)

    if handler is None:

        raise ValueError(
            f"Unknown destination: {destination}"
        )

    return handler(item)


# --------------------------------------------------
# Source Button
# --------------------------------------------------

def build_source_button(item):

    source = item.get(
        "source_url",
        ""
    )

    if not source:
        return None

    return json.dumps({

        "inline_keyboard": [

            [
                {
                    "text": "📰 Read Source",
                    "url": source
                }
            ]

        ]

    })

# --------------------------------------------------
# Telegram Publisher
# --------------------------------------------------

def publish_to_telegram(item):

    print("=" * 60)
    print("PUBLISHING TO TELEGRAM")
    print("Type :", item.get("type"))
    print("Image:", item.get("image"))
    print("=" * 60)

    post_type = item.get("type")

    reply_markup = build_source_button(item)

    # -----------------------------------------
    # Poll
    # -----------------------------------------

    if post_type == "what_if":

        ok = send_poll(
            BOT_TOKEN,
            PUBLIC_CHAT_ID,
            item["question"],
            item["options"]
        )

        if not ok:
            raise Exception("Poll publishing failed.")

    # -----------------------------------------
    # Photo
    # -----------------------------------------

    elif item.get("image"):

        send_photo(
            BOT_TOKEN,
            PUBLIC_CHAT_ID,
            item["image"],
            item.get("text", ""),
            reply_markup,
            post_type
        )

    # -----------------------------------------
    # Text
    # -----------------------------------------

    else:

        send_telegram(
            BOT_TOKEN,
            PUBLIC_CHAT_ID,
            item.get("text", ""),
            post_type,
            reply_markup
        )

    return {

        "success": True,

        "telegram": True,

        "x_text": item.get("text", ""),

        "image": item.get("image"),

        "type": post_type

    }

# --------------------------------------------------
# X Publisher
# --------------------------------------------------

def publish_to_x(item):

    print("=" * 60)
    print("PREPARING X POST")
    print("Type :", item.get("type"))
    print("=" * 60)

    post_type = item.get("type")

    text = item.get("text", "")

    image = item.get("image")

    # -----------------------------------------
    # Future-proof image selection
    # -----------------------------------------

    if post_type == "x_funny":

        image = item.get("image")

    elif post_type == "x_educational":

        image = item.get("image")

    elif post_type == "x_viral":

        image = item.get("image")

    return {

        "success": True,

        "telegram": False,

        "x_text": text,

        "image": image,

        "type": post_type

    }

# --------------------------------------------------
# Telegram + X
# --------------------------------------------------

def publish_to_both(item):

    print("=" * 60)
    print("PUBLISHING TO BOTH")
    print("=" * 60)

    telegram_result = publish_to_telegram(item)

    x_result = publish_to_x(item)

    print("✓ Telegram prepared")
    print("✓ X prepared")

    return {

        "success": True,

        "telegram": telegram_result.get(
            "success",
            False
        ),

        "x_text": x_result.get(
            "x_text",
            ""
        ),

        "image": x_result.get(
            "image"
        ),

        "type": x_result.get(
            "type",
            item.get("type")
        )

    }