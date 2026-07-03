import os

from modules import (
    send_telegram,
    send_photo,
    send_poll
)

PUBLIC_CHAT_ID = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def publish(item, destination="telegram"):
    """
    Central publishing dispatcher.

    Supported destinations:
    - telegram
    - x
    - both
    """

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

        return

    if item.get("image"):

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


def publish_to_x(item):
    """
    Free-mode X publishing.

    Returns the content instead of posting it.
    """

    return {
        "title": "🐦 X POST READY",
        "text": item.get("text", ""),
        "image": item.get("image")
    }


def publish_to_both(item):

    publish_to_telegram(item)

    return publish_to_x(item)
