import csv
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configs
CSV_FILE = 'up.csv'
OUTPUT_FILE = 'updated_dawn_articles.json'
CHECKPOINT_FILE = 'checkpoint_new.json'
MAX_WORKERS = 3
MAX_RETRIES = 70  # Maximum retry attempts for each article
CHECKPOINT_EVERY = 150
REQUEST_DELAY = 0.2  # small delay to avoid rapid-fire

# Rotating User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Edge/91.0.864.59"
]

# More Browser-like headers
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.dawn.com/",
}

# Use session to persist cookies and headers
session = requests.Session()

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def fetch_article_content(url):
    """
    Fetch the article content from a given URL.
    This function keeps retrying until it succeeds.
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Update session headers with a random User-Agent for each request
            session.headers.update({
                "User-Agent": get_random_user_agent()
            })
            
            response = session.get(url, timeout=10)
            
            # If a 403 error is returned, retry after a delay
            if response.status_code == 403:
                print(f"⚠️ 403 Forbidden: Retrying {url} after delay...")
                retries += 1
                time.sleep(0.2)
                continue

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to extract the content by inspecting the HTML structure of the page
                content_div = soup.find('div', class_='story__content')  # This class should be correct
                if content_div:
                    paragraphs = content_div.find_all('p')
                    return ' '.join([p.get_text(strip=True) for p in paragraphs])
                else:
                    print(f"⚠️ No content div found for {url}")
                    return "Content not found"
            else:
                print(f"⚠️ [{response.status_code}] for {url}")
                retries += 1
                time.sleep(0.2)
        except requests.exceptions.RequestException as e:
            print(f"❌ Exception on {url}: {e}")
            retries += 1
            time.sleep(0.2)
    
    return "Failed to fetch content after maximum retries"

def read_csv(filename=CSV_FILE):
    """
    Reads a CSV file and returns a list of articles.
    Each article is represented as a dictionary.
    """
    articles = []
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            articles.append(row)
    return articles

def save_to_json(data, filename):
    """
    Saves the provided data to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def process_article(article):
    """
    Processes an article by fetching its content.
    """
    content = fetch_article_content(article['link'])
    article['content'] = content
    article.pop('link', None)
    return article

def update_articles_with_content(articles):
    """
    Updates articles by adding the content fetched from their URLs.
    Uses threading to speed up processing.
    """
    updated_articles = []
    total = len(articles)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_article, article): idx for idx, article in enumerate(articles, 1)}

        for future in as_completed(futures):
            idx = futures[future]
            try:
                updated = future.result()
                updated_articles.append(updated)
                print(f"[{idx}/{total}] ✅ Processed: {updated.get('title', 'No title')}")
            except Exception as e:
                print(f"[{idx}/{total}] ❌ Error: {e}")

            if idx % CHECKPOINT_EVERY == 0:
                print(f"💾 Checkpoint at {idx} articles")
                save_to_json(updated_articles, CHECKPOINT_FILE)

    return updated_articles

def main():
    """
    The main function that loads articles, processes them, and saves the result.
    """
    print("📥 Loading articles...")
    articles = read_csv(CSV_FILE)

    if not articles:
        print("❌ No articles found. Exiting.")
        return

    print(f"🚀 Processing {len(articles)} articles using {MAX_WORKERS} threads...\n")
    updated_articles = update_articles_with_content(articles)

    print(f"\n💾 Final save to {OUTPUT_FILE}")
    save_to_json(updated_articles, OUTPUT_FILE)
    print("✅ All done!")

if __name__ == '__main__':
    main()
