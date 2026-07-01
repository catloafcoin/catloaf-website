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
