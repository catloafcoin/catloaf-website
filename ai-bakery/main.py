import feedparser
from google import genai
from config import GEMINI_API_KEY

# Load RSS feeds
with open("rss_feeds.txt", "r") as f:
    feeds = [line.strip() for line in f if line.strip()]

articles = []

for feed in feeds:
    try:
        rss = feedparser.parse(feed)
        for entry in rss.entries[:3]:
            articles.append(
                f"Title: {entry.get('title','')}\n"
                f"Summary: {entry.get('summary','')}\n"
            )
    except Exception:
        pass

news = "\n\n".join(articles[:15])

# Load CatLoaf personality
with open("prompt.txt", "r") as f:
    system_prompt = f.read()

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""
{system_prompt}

Today's news:

{news}

Generate:

1. One X post
2. One Telegram post
3. One engagement question
4. One image prompt in CatLoaf style
5. Best posting time (IST)
"""
)

print(response.text)
