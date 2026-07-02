import os
import requests
import time

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def get_updates(offset=None):
    params = {}

    if offset:
        params["offset"] = offset

    r = requests.get(f"{API}/getUpdates", params=params, timeout=30)
    return r.json()


def answer_callback(callback_id, text):
    requests.post(
        f"{API}/answerCallbackQuery",
        data={
            "callback_query_id": callback_id,
            "text": text,
            "show_alert": False
        }
    )


def edit_message(chat_id, message_id, text):
    requests.post(
        f"{API}/editMessageText",
        data={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
    )


print("Admin Bot Started")

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

        print("Button pressed:", data)

        answer_callback(
            callback["id"],
            f"Received: {data}"
        )

        edit_message(
            chat_id,
            message_id,
            f"✅ Button received:\n\n{data}"
        )

    time.sleep(1)
