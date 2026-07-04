import feedparser


# --------------------------------------------------
# RSS Reader
# --------------------------------------------------

def get_latest_news(
    feed_file="rss_feeds.txt",
    max_articles=20
):

    articles = []

    try:

        with open(
            feed_file,
            "r",
            encoding="utf-8"
        ) as f:

            feeds = [
                line.strip()
                for line in f
                if line.strip()
            ]

    except FileNotFoundError:

        print(
            f"RSS feed file not found: {feed_file}"
        )

        return []

    # ----------------------------------------
    # Read every RSS feed
    # ----------------------------------------

    for url in feeds:

        try:

            feed = feedparser.parse(url)

            source = feed.feed.get(
                "title",
                url
            )

            for entry in feed.entries[:5]:

                image = ""

                # ----------------------------
                # media:content
                # ----------------------------

                if (
                    "media_content" in entry
                    and entry.media_content
                ):

                    image = (
                        entry.media_content[0]
                        .get("url", "")
                    )

                # ----------------------------
                # media:thumbnail
                # ----------------------------

                elif (
                    "media_thumbnail" in entry
                    and entry.media_thumbnail
                ):

                    image = (
                        entry.media_thumbnail[0]
                        .get("url", "")
                    )

                # ----------------------------
                # enclosure
                # ----------------------------

                elif "links" in entry:

                    for link in entry.links:

                        if (
                            link.get(
                                "type",
                                ""
                            ).startswith("image/")
                            or link.get("rel") == "enclosure"
                        ):

                            image = link.get(
                                "href",
                                ""
                            )

                            break

                articles.append({

                    "title":
                        entry.get(
                            "title",
                            ""
                        ),

                    "summary":
                        entry.get(
                            "summary",
                            entry.get(
                                "description",
                                ""
                            )
                        ),

                    "link":
                        entry.get(
                            "link",
                            ""
                        ),

                    "source":
                        source,

                    "image":
                        image

                })

        except Exception as e:

            print(
                f"Failed reading {url}: {e}"
            )

            continue

    # ----------------------------------------
    # Remove duplicate titles
    # ----------------------------------------

    unique = []
    seen = set()

    for article in articles:

        key = (
            article["title"]
            .strip()
            .lower()
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(article)

    print(
        f"Loaded {len(unique)} unique articles."
    )

    return unique[:max_articles]

# --------------------------------------------------
# Article Scoring
# --------------------------------------------------

def score_articles(articles):

    keywords = {

        # ----------------------------
        # Core Solana
        # ----------------------------

        "solana": 30,
        "validator": 18,
        "firedancer": 22,
        "jupiter": 20,
        "raydium": 20,
        "pump.fun": 20,
        "phantom": 18,
        "backpack": 18,
        "drift": 18,
        "sanctum": 18,
        "kamino": 18,
        "marinade": 18,

        # ----------------------------
        # Builders
        # ----------------------------

        "builder": 15,
        "developer": 15,
        "ecosystem": 15,
        "infrastructure": 15,
        "rpc": 12,
        "sdk": 12,

        # ----------------------------
        # Trading
        # ----------------------------

        "launch": 15,
        "listing": 15,
        "airdrop": 12,
        "upgrade": 15,
        "integration": 15,
        "volume": 12,
        "liquidity": 12,

        # ----------------------------
        # Memecoins
        # ----------------------------

        "memecoin": 12,
        "meme": 10,
        "community": 8,

        # ----------------------------
        # Security
        # ----------------------------

        "hack": 25,
        "exploit": 25,
        "security": 20,

        # ----------------------------
        # Institutional
        # ----------------------------

        "etf": 20,
        "institutional": 18,
        "adoption": 15,
        "payments": 12,
        "stablecoin": 12
    }

    trusted_sources = [

        "solana",

        "cointelegraph",

        "coindesk",

        "decrypt",

        "the block",

        "blockworks",

        "messari",

        "helius",

        "jupiter",

        "raydium",

        "phantom"

    ]

    scored = []

    for article in articles:

        score = 0

        text = (
            article.get("title", "")
            + " "
            + article.get("summary", "")
        ).lower()

        # ----------------------------------------
        # Keyword scoring
        # ----------------------------------------

        for word, value in keywords.items():

            if word in text:
                score += value

        # ----------------------------------------
        # Prefer articles with images
        # ----------------------------------------

        if article.get("image"):
            score += 8

        # ----------------------------------------
        # Prefer trusted sources
        # ----------------------------------------

        source = article.get(
            "source",
            ""
        ).lower()

        for trusted in trusted_sources:

            if trusted in source:

                score += 5
                break

        # ----------------------------------------
        # Headline quality bonus
        # ----------------------------------------

        title = article.get(
            "title",
            ""
        )

        if len(title) > 40:
            score += 2

        # ----------------------------------------
        # High-impact phrases
        # ----------------------------------------

        impact_words = [

            "breaking",
            "major",
            "launch",
            "released",
            "upgrade",
            "partnership",
            "integration",
            "record",
            "new"

        ]

        for word in impact_words:

            if word in text:
                score += 3

        # ----------------------------------------
        # Ignore weak articles
        # ----------------------------------------

        if score < 5:
            continue

        article["score"] = score

        scored.append(article)

    # ----------------------------------------
    # Sort by score (highest first)
    # ----------------------------------------

    scored.sort(
        key=lambda article: (
            article["score"],
            bool(article.get("image"))
        ),
        reverse=True
    )

    print("\n" + "=" * 60)
    print("TOP SCORED ARTICLES")
    print("=" * 60)

    for article in scored[:10]:

        print(
            f"[{article['score']:>3}] "
            f"{'🖼️' if article.get('image') else '📄'} "
            f"{article.get('source', 'Unknown')} "
            f"- {article.get('title', '')}"
        )

    print("=" * 60)

    return scored