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


# --------------------------------------------------
# Telegram Helpers
# --------------------------------------------------

def get_updates(offset=None):

    params = {}

    if offset is not None:
        params["offset"] = offset

    try:

        response = requests.get(
            f"{API}/getUpdates",
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        print("=" * 60)
        print("GET UPDATES FAILED")
        print(e)
        print("=" * 60)

        return {
            "ok": False,
            "result": []
        }


def answer_callback(callback_id, text):

    try:

        requests.post(
            f"{API}/answerCallbackQuery",
            data={
                "callback_query_id": callback_id,
                "text": text
            },
            timeout=20
        )

    except Exception as e:

        print("Callback answer failed:", e)


def send_admin_message(chat_id, text):

    try:

        requests.post(
            f"{API}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            },
            timeout=20
        )

    except Exception as e:

        print("Admin message failed:", e)


def send_admin_photo(chat_id, image, caption=""):

    if not image:
        return

    payload = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "HTML"
    }

    # ------------------------------------------
    # Remote image
    # ------------------------------------------

    if (
        isinstance(image, str)
        and (
            image.startswith("http://")
            or image.startswith("https://")
        )
    ):

        payload["photo"] = image

        try:

            requests.post(
                f"{API}/sendPhoto",
                data=payload,
                timeout=60
            )

        except Exception as e:

            print("Remote admin image failed:", e)

        return

    # ------------------------------------------
    # Local image
    # ------------------------------------------

    try:

        with open(image, "rb") as photo:

            requests.post(
                f"{API}/sendPhoto",
                data=payload,
                files={
                    "photo": photo
                },
                timeout=60
            )

    except Exception as e:

        print("Local admin image failed:", e)


# --------------------------------------------------
# Queue Helper
# --------------------------------------------------

def find_queue_item(post_id):

    try:

        queue = get_queue()

        return next(

            (
                item
                for item in queue
                if item["id"] == post_id
            ),

            None

        )

    except Exception as e:

        print("=" * 60)
        print("QUEUE LOOKUP FAILED")
        print(e)
        print("=" * 60)

        return None

# --------------------------------------------------
# Keyboard Helpers
# --------------------------------------------------

def show_destination_menu(chat_id, message_id, post_id):

    keyboard = {

        "inline_keyboard": [

            [
                {
                    "text": "📣 Telegram",
                    "callback_data": f"tg_{post_id}"
                },
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
                    "text": "⬅ Back",
                    "callback_data": f"cancel_{post_id}"
                }
            ]

        ]

    }

    try:

        requests.post(

            f"{API}/editMessageReplyMarkup",

            data={
                "chat_id": chat_id,
                "message_id": message_id,
                "reply_markup": json.dumps(keyboard)
            },

            timeout=20

        )

    except Exception as e:

        print("Destination menu failed:", e)


def restore_main_buttons(chat_id, message_id, post_id):

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

    try:

        requests.post(

            f"{API}/editMessageReplyMarkup",

            data={
                "chat_id": chat_id,
                "message_id": message_id,
                "reply_markup": json.dumps(keyboard)
            },

            timeout=20

        )

    except Exception as e:

        print("Restore keyboard failed:", e)


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

    try:

        requests.post(

            f"{API}/editMessageReplyMarkup",

            data={
                "chat_id": chat_id,
                "message_id": message_id,
                "reply_markup": json.dumps(keyboard)
            },

            timeout=20

        )

    except Exception as e:

        print("Edit keyboard failed:", e)


# --------------------------------------------------
# Main Loop
# --------------------------------------------------

offset = None

print("=" * 60)
print("🍞 CatLoaf Approval Bot Running...")
print("=" * 60)

while True:

    updates = get_updates(offset)

    if not updates.get("ok"):

        time.sleep(2)
        continue

    for update in updates.get("result", []):

        try:

            offset = update["update_id"] + 1

            if "callback_query" not in update:
                continue

            callback = update["callback_query"]

            data = callback["data"]

            chat_id = callback["message"]["chat"]["id"]

            message_id = callback["message"]["message_id"]

            print("=" * 60)
            print("BUTTON PRESSED")
            print("Data :", data)
            print("Chat :", chat_id)
            print("=" * 60)

            # ------------------------------------------
            # APPROVE
            # ------------------------------------------

            if data.startswith("approve_"):

                post_id = data.replace(
                    "approve_",
                    ""
                )

                show_destination_menu(
                    chat_id,
                    message_id,
                    post_id
                )

                answer_callback(
                    callback["id"],
                    "Choose where to publish"
                )

            # ------------------------------------------
            # TELEGRAM
            # ------------------------------------------

            elif data.startswith("tg_"):

                post_id = data.replace(
                    "tg_",
                    ""
                )

                item = find_queue_item(post_id)

                if item is None:

                    answer_callback(
                        callback["id"],
                        "❌ Post not found."
                    )

                    continue

                result = publish(
                    item,
                    "telegram"
                )

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
                    "Published!"
                )

            # ------------------------------------------
            # X
            # ------------------------------------------

            elif data.startswith("x_"):

                post_id = data.replace(
                    "x_",
                    ""
                )

                item = find_queue_item(post_id)

                if item is None:

                    answer_callback(
                        callback["id"],
                        "❌ Post not found."
                    )

                    continue

                result = publish(
                    item,
                    "x"
                )

                if result.get("image"):

                    send_admin_photo(
                        chat_id,
                        result["image"],
                        "🐦 Image for X Post"
                    )

                if result.get("x_text"):

                    send_admin_message(
                        chat_id,
                        (
                            "🐦 <b>X POST READY</b>\n\n"
                            f"{result['x_text']}"
                        )
                    )

                mark_posted(post_id)

                remove_pending(post_id)

                remove_by_id(post_id)

                edit_buttons(
                    chat_id,
                    message_id,
                    "✅ X Draft Ready"
                )

                answer_callback(
                    callback["id"],
                    "X draft created."
                )

            # ------------------------------------------
            # BOTH
            # ------------------------------------------

            elif data.startswith("both_"):

                post_id = data.replace(
                    "both_",
                    ""
                )

                item = find_queue_item(post_id)

                if item is None:

                    answer_callback(
                        callback["id"],
                        "❌ Post not found."
                    )

                    continue

                result = publish(
                    item,
                    "both"
                )

                if result.get("image"):

                    send_admin_photo(
                        chat_id,
                        result["image"],
                        "🐦 Image for X Post"
                    )

                if result.get("x_text"):

                    send_admin_message(
                        chat_id,
                        (
                            "🐦 <b>X POST READY</b>\n\n"
                            f"{result['x_text']}"
                        )
                    )

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
                    "Published!"
                )

            # ------------------------------------------
            # BACK
            # ------------------------------------------

            elif data.startswith("cancel_"):

                post_id = data.replace(
                    "cancel_",
                    ""
                )

                restore_main_buttons(
                    chat_id,
                    message_id,
                    post_id
                )

                answer_callback(
                    callback["id"],
                    "Cancelled"
                )

            # ------------------------------------------
            # REJECT
            # ------------------------------------------

            elif data.startswith("reject_"):

                post_id = data.replace(
                    "reject_",
                    ""
                )

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

                print(
                    f"Rejected: {post_id}"
                )

            # ------------------------------------------
            # EDIT
            # ------------------------------------------

            elif data.startswith("edit_"):

                answer_callback(
                    callback["id"],
                    "✏️ Editing coming soon."
                )

            # ------------------------------------------
            # REGENERATE
            # ------------------------------------------

            elif data.startswith("regen_"):

                answer_callback(
                    callback["id"],
                    "🔄 Regeneration coming soon."
                )

            # ------------------------------------------
            # UNKNOWN
            # ------------------------------------------

            else:

                answer_callback(
                    callback["id"],
                    "Unknown action."
                )

        except Exception as e:

            print("=" * 60)
            print("UNHANDLED CALLBACK ERROR")
            print(e)
            print("=" * 60)

            try:

                answer_callback(
                    callback["id"],
                    "❌ Something went wrong."
                )

            except Exception:
                pass

    time.sleep(1)