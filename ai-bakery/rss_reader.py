import feedparser


def get_latest_news(feed_file="rss_feeds.txt", max_articles=10):

    articles = []

    try:

        with open(feed_file, "r", encoding="utf-8") as f:
            feeds = [
                line.strip()
                for line in f
                if line.strip()
            ]

    except FileNotFoundError:

        print(f"RSS feed file not found: {feed_file}")
        return []

    for url in feeds:

        try:

            feed = feedparser.parse(url)

            source = feed.feed.get("title", url)

            for entry in feed.entries[:3]:

                image = ""

                # RSS media:content
                if (
                    "media_content" in entry
                    and entry.media_content
                ):
                    image = entry.media_content[0].get(
                        "url",
                        ""
                    )

                # RSS media:thumbnail
                elif (
                    "media_thumbnail" in entry
                    and entry.media_thumbnail
                ):
                    image = entry.media_thumbnail[0].get(
                        "url",
                        ""
                    )

                # RSS enclosure/image
                elif "links" in entry:

                    for link in entry.links:

                        if (
                            link.get("type", "").startswith("image/")
                            or link.get("rel") == "enclosure"
                        ):

                            image = link.get(
                                "href",
                                ""
                            )

                            break

                articles.append({

                    "title": entry.get(
                        "title",
                        ""
                    ),

                    "summary": entry.get(
                        "summary",
                        entry.get(
                            "description",
                            ""
                        )
                    ),

                    "link": entry.get(
                        "link",
                        ""
                    ),

                    "source": source,

                    "image": image

                })

        except Exception as e:

            print(
                f"Failed to read feed {url}: {e}"
            )

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
        "integration": 10,
        "launch": 10,
        "upgrade": 10,
        "volume": 10,

        "hack": 25,
        "exploit": 25,
        "security": 20,
        "validator": 15,

        "etf": 25,
        "institutional": 20,

        "meme": 5,
        "memecoin": 5,
        "community": 5
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

        # Boost articles with images
        if article.get("image"):
            score += 2

        # Slight boost for official sources
        source = article.get("source", "").lower()

        trusted_sources = [
            "solana",
            "cointelegraph",
            "the block",
            "decrypt",
            "coindesk"
        ]

        for trusted in trusted_sources:

            if trusted in source:
                score += 3
                break

        article["score"] = score

        scored.append(article)

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return scored