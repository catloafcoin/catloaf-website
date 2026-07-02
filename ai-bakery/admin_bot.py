import os
import time
import json
import requests

from scheduler import (
    get_queue,
    remove_by_id,
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


def show_destination_menu(chat_id, message_id, post_id):

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "📣 Telegram",
                    "callback_data": f"tg_{post_id}"
                }
            ],
            [
                {
                    "text": "🐦 X",
                    "callback_data": f"x_{post_id}"
                }
            ],
            [
                {
                    "text": "🌍 Both",
                    "callback_data": f"both_{post_id}"
                }
            ],
            [
                {
                    "text": "⬅ Cancel",
                    "callback_data": f"cancel_{post_id}"
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


def edit_buttons(chat_id, message_id, text):

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": text,
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

        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]

        print("Pressed:", data)

        if data.startswith("approve_"):

            post_id = data.replace("approve_", "")

            show_destination_menu(
                chat_id,
                message_id,
                post_id
            )

            answer_callback(
                callback["id"],
                "Choose destination"
            )

        elif data.startswith("tg_"):

            post_id = data.replace("tg_", "")

            queue = get_queue()

            item = next(
                (q for q in queue if q["id"] == post_id),
                None
            )

            if item:

                publish(item, "telegram")

                mark_posted(post_id)
                remove_pending(post_id)
                remove_by_id(post_id)

                edit_buttons(
                    chat_id,
                    message_id,
                    "✅ Published to Telegram"
                )

                answer_callback(
                    callback["id"],
                    "Published"
                )

        elif data.startswith("x_"):

            post_id = data.replace("x_", "")

            queue = get_queue()

            item = next(
                (q for q in queue if q["id"] == post_id),
                None
            )

            if item:

                publish(item, "x")

                mark_posted(post_id)
                remove_pending(post_id)
                remove_by_id(post_id)

                edit_buttons(
                    chat_id,
                    message_id,
                    "✅ Published to X"
                )

                answer_callback(
                    callback["id"],
                    "Published"
                )

        elif data.startswith("both_"):

            post_id = data.replace("both_", "")

            queue = get_queue()

            item = next(
                (q for q in queue if q["id"] == post_id),
                None
            )

            if item:

                publish(item, "both")

                mark_posted(post_id)
                remove_pending(post_id)
                remove_by_id(post_id)

                edit_buttons(
                    chat_id,
                    message_id,
                    "✅ Published to Telegram & X"
                )

                answer_callback(
                    callback["id"],
                    "Published"
                )

        elif data.startswith("cancel_"):

            post_id = data.replace("cancel_", "")

            keyboard = {
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
            }

            requests.post(
                f"{API}/editMessageReplyMarkup",
                data={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "reply_markup": json.dumps(keyboard)
                }
            )

            answer_callback(
                callback["id"],
                "Cancelled"
            )

        elif data.startswith("reject_"):

            post_id = data.replace("reject_", "")

            remove_pending(post_id)
            remove_by_id(post_id)

            edit_buttons(
                chat_id,
                message_id,
                "❌ Rejected"
            )

            answer_callback(
                callback["id"],
                "Rejected"
            )

        else:

            answer_callback(
                callback["id"],
                "Received 👍"
            )

    time.sleep(1)
