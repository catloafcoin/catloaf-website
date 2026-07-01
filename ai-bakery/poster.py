from scheduler import get_queue, remove_first, should_post_now
from modules import send_telegram

def process_queue():
    queue = get_queue()

    if not queue:
        print("No queued content.")
        return

    if not should_post_now():
        print("Not time to post yet.")
         return

    item = queue[0]

    print("Processing first queued item...")

    send_telegram(item)
    print("✓ Sent to Telegram")

    remove_first()

    print("✓ Queue updated")

    if __name__ == "__main__":
    process_queue()
