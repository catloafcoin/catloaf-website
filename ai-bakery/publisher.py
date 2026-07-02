import os

from modules import send_telegram, send_photo, send_poll

PUBLIC_CHAT_ID = os.getenv("TELEGRAM_PUBLIC_CHAT_ID")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def publish(item, destination="telegram"):

    post_type = item.get("type")

    # -------------------------
    # Telegram
    # -------------------------

    if destination in ["telegram", "both"]:

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

    # -------------------------
    # X (Coming Next)
    # -------------------------

    if destination in ["x", "both"]:

        print(f"Publishing to X: {post_type}")

        # TODO:
        # post_to_x(item)
