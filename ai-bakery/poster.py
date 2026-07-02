from scheduler import get_queue, remove_first, should_post_now, load_posted, mark_posted
from modules import send_telegram, send_photo, send_poll
import os

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
                item.get("text", "")
            )

        else:

            send_telegram(
                TELEGRAM_BOT_TOKEN,
                TELEGRAM_CHAT_ID,
                item.get("text", ""),
                post_type
            )

        print("✓ Sent")

        mark_posted(post_id)

        remove_first()

        print("✓ Queue updated")
        
if __name__ == "__main__":
    process_queue()
