import json
import os
from modules.rss_fetcher import fetch_rss_feed
from modules.llm_processor import process_article_with_llm
from modules.output_formatter import create_structured_output

OUTPUT_FILE = "data/processed_articles.jsonl"
FEED_URL = "http://feeds.bbci.co.uk/news/rss.xml"


def load_processed_guids():
    """Reads the output file to find which articles have already been processed."""
    processed_guids = set()
    if not os.path.exists(OUTPUT_FILE):
        return processed_guids

    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("status") == "success":
                    # Use link as the unique identifier
                    processed_guids.add(data["data"]["link"])
            except json.JSONDecodeError:
                continue  # Ignore corrupted lines
    print(f"Found {len(processed_guids)} previously processed articles.")
    return processed_guids


def main():
    """The main function to run the NewsStream processor."""
    print("--- 🚀 Starting NewsStream Processor ---")

    # 1. Load GUIDs of already processed articles
    processed_article_guids = load_processed_guids()

    # 2. Fetch the latest articles from the feed
    feed = fetch_rss_feed(FEED_URL)
    if not feed:
        print("--- 🛑 Halting due to feed fetch failure. ---")
        return

    # 3. Filter out articles that have already been processed
    new_articles = [
        article for article in feed.entries
        if article.link not in processed_article_guids
    ]

    if not new_articles:
        print("--- ✅ No new articles to process. ---")
        return

    print(f"📰 Found {len(new_articles)} new articles to process.")

    for article in new_articles:
        original_data = {
            "title": article.title,
            "link": article.link,
            "published": article.get("published"),
        }
        print(f"\nProcessing article: '{article.title}'")

        try:
            llm_data = process_article_with_llm(article.title, article.summary)
            final_json_output = create_structured_output(
                status="success",
                data=llm_data,
                original_data=original_data
            )
        except Exception as e:
            print(f"❗️ An error occurred: {e}")
            final_json_output = create_structured_output(
                status="error",
                error_message=str(e),
                original_data=original_data
            )

        # 4. Append the new record to the file
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(final_json_output) + '\n')

    print(f"\n--- ✅ NewsStream Processor Finished. Results saved to {OUTPUT_FILE} ---")


if __name__ == "__main__":
    main()