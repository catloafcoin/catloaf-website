import os
import time
import json
import requests

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

        answer_callback(
            callback["id"],
            "Received 👍"
        )

        edit_buttons(
            callback["message"]["chat"]["id"],
            callback["message"]["message_id"]
        )

    time.sleep(1)
