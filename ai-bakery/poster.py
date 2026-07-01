from scheduler import get_queue, remove_first, should_post_now, load_posted, mark_posted
from modules import send_telegram
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def process_queue():
    queue = get_queue()

    if not queue:
        print("No queued content.")
        return

    if not should_post_now():
        print("Not time to post yet.")
        return

    item = queue[0]
    post_id = item.get("id", "")

    posted = load_posted()

    if post_id in posted:
        print("Already posted.")
        remove_first()
        return

    print("Processing first queued item...")

    send_telegram(item)
    print("✓ Sent to Telegram")

    mark_posted(post_id)
    print("✓ Added to posted history")

    remove_first()
    print("✓ Queue updated")


if __name__ == "__main__":
    process_queue()
