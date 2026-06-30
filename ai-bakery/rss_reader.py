import feedparser

def get_latest_news(feed_file="rss_feeds.txt", max_articles=10):
    articles = []

    with open(feed_file, "r") as f:
        feeds = [line.strip() for line in f if line.strip()]

    for url in feeds:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:3]:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "source": feed.feed.get("title", url)
                })
        except Exception:
            continue

    return articles[:max_articles]
