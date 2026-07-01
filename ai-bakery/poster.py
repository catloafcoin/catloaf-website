from scheduler import get_queue, remove_first

def process_queue():
    queue = get_queue()

    if not queue:
        print("No queued content.")
        return

    item = queue[0]

    print("Processing first queued item...")

    # Later we'll send Telegram here

    remove_first()

    print("✓ Queue updated")
