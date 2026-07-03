import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("SUPABASE_URL exists:", bool(SUPABASE_URL))
print("SUPABASE_SERVICE_ROLE_KEY exists:", bool(SUPABASE_KEY))

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL environment variable is missing")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY environment variable is missing")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def add_queue(item):
    supabase.table("queue").upsert(item).execute()


def get_queue():
    return supabase.table("queue").select("*").execute().data


def remove_queue(post_id):
    supabase.table("queue").delete().eq("id", post_id).execute()


def add_pending(post_id):
    supabase.table("pending_posts").upsert({"id": post_id}).execute()


def remove_pending(post_id):
    supabase.table("pending_posts").delete().eq("id", post_id).execute()


def add_posted(post_id):
    supabase.table("posted_posts").upsert({"id": post_id}).execute()


def is_posted(post_id):
    data = (
        supabase.table("posted_posts")
        .select("id")
        .eq("id", post_id)
        .execute()
        .data
    )

    return len(data) > 0
