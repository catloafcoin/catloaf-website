import os

from modules import (
    send_telegram,
    send_photo,
    send_poll
)

PUBLIC_CHAT_ID = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def publish(item, destination="telegram"):

    handlers = {
        "telegram": publish_to_telegram,
        "x": publish_to_x,
        "both": publish_to_both
    }

    handler = handlers.get(destination)

    if not handler:
        raise ValueError(f"Unknown destination: {destination}")

    return handler(item)


def publish_to_telegram(item):

    post_type = item.get("type")

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
            item.get("text", "")
        )

    else:

        send_telegram(
            BOT_TOKEN,
            PUBLIC_CHAT_ID,
            item.get("text", ""),
            post_type
        )

    return {
        "success": True,
        "telegram": True,
        "x_text": None,
        "image": None
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
