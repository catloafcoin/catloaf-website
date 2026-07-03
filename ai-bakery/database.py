import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

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
