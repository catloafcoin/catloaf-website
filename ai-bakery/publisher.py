import os
import json

from modules import (
    send_telegram,
    send_photo,
    send_poll
)

PUBLIC_CHAT_ID = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def publish(item, destination="telegram"):

    print("=" * 60)
    print("PUBLISH CALLED")
    print("Destination:", destination)
    print("Item:", item)
    print("=" * 60)

    handlers = {
        "telegram": publish_to_telegram,
        "x": publish_to_x,
        "both": publish_to_both
    }

    handler = handlers.get(destination)

    if handler is None:
        raise ValueError(f"Unknown destination: {destination}")

    return handler(item)


def build_source_button(item):

    source = item.get("source_url", "")

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


def publish_to_telegram(item):

    print("publish_to_telegram()")

    post_type = item.get("type")

    reply_markup = build_source_button(item)

    if post_type == "what_if":

        send_poll(
            BOT_TOKEN,
            PUBLIC_CHAT_ID,
            item["question"],
            item["options"]
        )

    elif item.get("image"):

        send_photo(
            BOT_TOKEN,
            PUBLIC_CHAT_ID,
            item["image"],
            item.get("text", ""),
            reply_markup
        )

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
        "image": item.get("image")
    }


def publish_to_x(item):

    return {
        "success": True,
        "telegram": False,
        "x_text": item.get("text", ""),
        "image": item.get("image")
    }


def publish_to_both(item):

    publish_to_telegram(item)

    return {
        "success": True,
        "telegram": True,
        "x_text": item.get("text", ""),
        "image": item.get("image")
    }