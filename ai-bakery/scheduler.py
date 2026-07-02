import json
import os
from datetime import datetime

QUEUE_FILE = "news_queue.json"


def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)


def add_to_queue(item):
    queue = load_queue()
    queue.append(item)
    save_queue(queue)


def get_queue():
    return load_queue()


def clear_queue():
    save_queue([])


DAILY_FILE = "daily_content.json"


def save_daily(data):
    with open(DAILY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_daily():
    if not os.path.exists(DAILY_FILE):
        return {}

    with open(DAILY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def remove_first():
    queue = load_queue()

    if queue:
        queue.pop(0)

    save_queue(queue)


def remove_by_id(post_id):

    queue = load_queue()

    queue = [
        item
        for item in queue
        if item.get("id") != post_id
    ]

    save_queue(queue)


def should_post_now():
    """
    Placeholder scheduler.

    For now it always returns True.

    Later it will check:
    - Breaking news score
    - Best posting windows
    - Duplicate posts
    - Daily limits
    """

    return True


POSTED_FILE = "posted.json"
PENDING_FILE = "pending.json"


def load_posted():
    if not os.path.exists(POSTED_FILE):
        return []

    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_posted(data):
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def mark_posted(post_id):
    posted = load_posted()

    if post_id not in posted:
        posted.append(post_id)

    save_posted(posted)


def load_pending():
    if not os.path.exists(PENDING_FILE):
        return []

    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_pending(data):
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def mark_pending(post_id):
    pending = load_pending()

    if post_id not in pending:
        pending.append(post_id)

    save_pending(pending)


def remove_pending(post_id):
    pending = load_pending()

    if post_id in pending:
        pending.remove(post_id)

    save_pending(pending)


def calculate_score(item):
    """
    Scores today's generated content.
    """

    score = 50

    telegram = item.get("telegram", {})

    text = (
        telegram.get("opening", "")
        + " "
        + " ".join(telegram.get("bullets", []))
        + " "
        + telegram.get("why", "")
        + " "
        + telegram.get("question", "")
    ).lower()

    keywords = [
        "solana",
        "jupiter",
        "phantom",
        "pump.fun",
        "raydium",
        "drift",
        "sanctum",
        "backpack",
        "meme",
        "airdrop",
        "defi",
        "token",
        "launch",
        "listing",
        "partnership",
        "volume",
        "record",
        "breaking"
    ]

    for word in keywords:
        if word in text:
            score += 5

    if item.get("meme"):
        score += 10

    if item.get("poll"):
        score += 10

    return min(score, 100)
