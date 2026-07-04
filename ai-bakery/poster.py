from scheduler import (
    get_queue,
    should_post_now,
    load_posted,
    load_pending,
    mark_pending
)

from modules import (
    send_telegram,
    send_photo
)

import os
import json

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# --------------------------------------------------
# Approval Keyboard
# --------------------------------------------------

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


# --------------------------------------------------
# Poll Preview
# --------------------------------------------------

def build_poll_preview(item):

    text = "📊 <b>POLL APPROVAL</b>\n\n"

    text += f"<b>Question</b>\n{item['question']}\n\n"

    text += "<b>Options</b>\n"

    for option in item["options"]:
        text += f"• {option}\n"

    return text

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

        print("=" * 60)
        print(f"Preparing approval: {post_id}")
        print("Type :", item.get("type"))
        print("Image:", item.get("image"))
        print("=" * 60)

        reply_markup = approval_keyboard(
            post_id,
            item
        )

        post_type = item.get("type")
        image = item.get("image")

        try:

            # ------------------------------------
            # Poll Preview
            # ------------------------------------
            if post_type == "what_if":

                send_telegram(
                    TELEGRAM_BOT_TOKEN,
                    TELEGRAM_CHAT_ID,
                    build_poll_preview(item),
                    "poll",
                    reply_markup
                )

            # ------------------------------------
            # Any Image (Local OR RSS URL)
            # ------------------------------------
            elif image is not None:

                print("=" * 60)
                print("Sending image approval")
                print("Post ID :", post_id)
                print("Type    :", post_type)
                print("Image   :", image)
                print("Caption :", item.get("text", "")[:80])
                print("=" * 60)

                send_photo(
                    TELEGRAM_BOT_TOKEN,
                    TELEGRAM_CHAT_ID,
                    image,
                    item.get("text", ""),
                    reply_markup,
                    post_type
                )

                print("✓ Image approval sent")

            # ------------------------------------
            # Text Post
            # ------------------------------------
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
            print("Type:", post_type)
            print(e)
            print("=" * 60)

    print("=" * 60)
    print("✓ Finished sending approval queue.")
    print("=" * 60)

if __name__ == "__main__":

    process_queue()