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
