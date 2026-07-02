import os
import time
import json
import requests

from scheduler import (
    get_queue,
    remove_first,
    mark_posted,
    remove_pending
)
from publisher import publish

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def get_updates(offset=None):
    params = {}

    if offset:
        params["offset"] = offset

    r = requests.get(
        f"{API}/getUpdates",
        params=params,
        timeout=30
    )

    return r.json()


def answer_callback(callback_id, text):
    requests.post(
        f"{API}/answerCallbackQuery",
        data={
            "callback_query_id": callback_id,
            "text": text
        }
    )


def edit_buttons(chat_id, message_id):

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "✅ Approved",
                    "callback_data": "done"
                }
            ]
        ]
    }

    requests.post(
        f"{API}/editMessageReplyMarkup",
        data={
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": json.dumps(keyboard)
        }
    )


print("CatLoaf Approval Bot Running...")

offset = None

while True:

    updates = get_updates(offset)

    if not updates["ok"]:
        time.sleep(2)
        continue

    for update in updates["result"]:

        offset = update["update_id"] + 1

        if "callback_query" not in update:
            continue

        callback = update["callback_query"]
        data = callback["data"]

        print("Pressed:", data)

        if data.startswith("approve_"):

            post_id = data.replace("approve_", "")

            queue = get_queue()

            item = next(
                (q for q in queue if q["id"] == post_id),
                None
            )

            if item:

                publish(item)

                mark_posted(post_id)

                remove_pending(post_id)

                remove_first()

                answer_callback(
                    callback["id"],
                    "Published ✅"
                )

            else:

                answer_callback(
                    callback["id"],
                    "Post not found."
                )

        elif data.startswith("reject_"):

            post_id = data.replace("reject_", "")

            remove_pending(post_id)

            remove_first()

            answer_callback(
                callback["id"],
                "Rejected ❌"
            )

        else:

            answer_callback(
                callback["id"],
                "Received 👍"
            )

        edit_buttons(
            callback["message"]["chat"]["id"],
            callback["message"]["message_id"]
        )

    time.sleep(1)
