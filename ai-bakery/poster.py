from scheduler import (
    get_queue,
    should_post_now,
    load_posted,
    load_pending,
    mark_pending
)

from modules import (
    send_telegram,
    send_photo,
    send_poll
)

import os
import json

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def approval_keyboard(post_id, item):

    rows = [
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

    if item.get("source_url"):

        rows.append([
            {
                "text": "📰 Read Source",
                "url": item["source_url"]
            }
        ])

    return json.dumps({
        "inline_keyboard": rows
    })


def process_queue():

    if not should_post_now():
        print("Not time to post yet.")
        return

    queue = get_queue()

    if not queue:
        print("Queue finished.")
        return

    posted = load_posted()
    pending = load_pending()

    for item in queue:

        post_id = item.get("id", "")

        if post_id in posted:
            print(f"Skipping published: {post_id}")
            continue

        if post_id in pending:
            print(f"Skipping pending: {post_id}")
            continue

        print(f"Preparing approval: {post_id}")

        reply_markup = approval_keyboard(
            post_id,
            item
        )

        post_type = item.get("type")

        image = item.get("image")

        try:

            # -----------------------------
            # Poll Approval
            # -----------------------------
            if post_type == "what_if":

                send_poll(
                    TELEGRAM_BOT_TOKEN,
                    TELEGRAM_CHAT_ID,
                    item["question"],
                    item["options"]
                )

            # -----------------------------
            # Photo Approval
            # -----------------------------
            elif image and os.path.exists(image):

                send_photo(
                    TELEGRAM_BOT_TOKEN,
                    TELEGRAM_CHAT_ID,
                    image,
                    item.get("text", ""),
                    reply_markup,
                    post_type
                )

            # -----------------------------
            # Text Approval
            # -----------------------------
            else:

                send_telegram(
                    TELEGRAM_BOT_TOKEN,
                    TELEGRAM_CHAT_ID,
                    item.get("text", ""),
                    post_type,
                    reply_markup
                )

            mark_pending(post_id)

            print(f"✓ Approval sent: {post_id}")

        except Exception as e:

            print("=" * 60)
            print("Approval Send Error")
            print("Post:", post_id)
            print(e)
            print("=" * 60)

    print("=" * 60)
    print("✓ Finished sending approval queue.")
    print("=" * 60)


if __name__ == "__main__":

    process_queue()