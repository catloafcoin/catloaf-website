from scheduler import (
    get_queue,
    remove_first,
    should_post_now,
    load_posted,
    mark_posted
)

from modules import send_telegram, send_photo, send_poll

import os
import json

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def process_queue():

    while True:

        queue = get_queue()

        if not queue:
            print("Queue finished.")
            break

        if not should_post_now():
            print("Not time to post yet.")
            break

        item = queue[0]

        post_id = item.get("id", "")

        posted = load_posted()

        if post_id in posted:
            print("Already posted.")
            remove_first()
            continue

        print(f"Posting: {item.get('type')}")

        reply_markup = json.dumps({
            "inline_keyboard": [
                [
                    {
                        "text": "✅ Approve",
                        "callback_data": f"approve_{post_id}"
                    },
                    {
                        "text": "❌ Reject",
                        "callback_data": f"reject_{post_id}"
                    }
                ],
                [
                    {
                        "text": "✏️ Edit",
                        "callback_data": f"edit_{post_id}"
                    },
                    {
                        "text": "🔄 Regenerate",
                        "callback_data": f"regen_{post_id}"
                    }
                ]
            ]
        })

        post_type = item.get("type")
        image = item.get("image")

        print(f"Image path: {image}")
        print(f"Image exists: {os.path.exists(image) if image else False}")

        if post_type == "what_if":

            send_poll(
                TELEGRAM_BOT_TOKEN,
                TELEGRAM_CHAT_ID,
                item["question"],
                item["options"]
            )

        elif image and os.path.exists(image):

            send_photo(
                TELEGRAM_BOT_TOKEN,
                TELEGRAM_CHAT_ID,
                image,
                item.get("text", ""),
                reply_markup
            )

        else:

            send_telegram(
                TELEGRAM_BOT_TOKEN,
                TELEGRAM_CHAT_ID,
                item.get("text", ""),
                post_type,
                reply_markup
            )

        print("✓ Sent")

        print("✓ Sent for approval")
        
        break

# Wait for admin approval before publishing


if __name__ == "__main__":
    process_queue()
