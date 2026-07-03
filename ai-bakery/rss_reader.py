import feedparser


def get_latest_news(feed_file="rss_feeds.txt", max_articles=10):
    articles = []

    try:

        with open(feed_file, "r", encoding="utf-8") as f:
            feeds = [line.strip() for line in f if line.strip()]

    except FileNotFoundError:
        print(f"RSS feed file not found: {feed_file}")
        return []

    for url in feeds:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:3]:

                articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get(
                        "summary",
                        entry.get("description", "")
                    ),
                    "link": entry.get("link", ""),
                    "source": feed.feed.get("title", url)
                })

        except Exception as e:
            print(f"Failed to read feed {url}: {e}")
            continue

    return articles[:max_articles]


def score_articles(articles):

    keywords = {
        "solana": 20,
        "jupiter": 15,
        "pump.fun": 15,
        "raydium": 15,
        "backpack": 15,
        "phantom": 15,
        "drift": 15,
        "sanctum": 15,
        "airdrop": 10,
        "listing": 10,
        "partnership": 10,
        "volume": 10,
        "launch": 10,
        "hack": 25,
        "exploit": 25,
        "security": 20,
        "etf": 25,
        "meme": 5,
        "memecoin": 5,
    }

    scored = []

    for article in articles:

        score = 0

        text = (
            article.get("title", "")
            + " "
            + article.get("summary", "")
        ).lower()

        for word, value in keywords.items():

            if word in text:
                score += value

        article["score"] = score
        scored.append(article)

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return scored