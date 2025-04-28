import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import threading
from tqdm import tqdm

# Define the base URL for article scraping
base_url = "https://jang.com.pk/news/"

# File paths
url_file = 'jang_national_articles.txt'
checkpoint_file = 'articles_checkpoint.json'

# Read URLs from the file
with open(url_file, 'r', encoding='utf-8') as file:
    article_urls = file.readlines()

# Clean up URLs
article_urls = [url.strip() for url in article_urls]

# Progress Bar and Checkpoint Update
def save_checkpoint(processed_articles):
    with open(checkpoint_file, 'w', encoding='utf-8') as checkpoint:
        json.dump(processed_articles, checkpoint, ensure_ascii=False, indent=4)

def scrape_article(url, processed_articles):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.find('h1').get_text(strip=True)

            # Extract date (from the last <div class="detail-time"> element)
            date_element = soup.find_all('div', class_='detail-time')[-1].get_text(strip=True)

            # Extract content (from the <div class="detail_view_content"> element)
            content = soup.find('div', class_='detail_view_content').get_text(strip=True)

            article_data = {
                'title': title,
                'date': date_element,
                'content': content,
                'url': url
            }

            # Save article data (you can save it in a list, database, or file)
            print(f"Successfully extracted article: {title}")
            
            processed_articles.append(article_data)

            # Update checkpoint after every 100 articles processed
            if len(processed_articles) % 100 == 0:
                save_checkpoint(processed_articles)
                print(f"Checkpoint updated after {len(processed_articles)} articles.")

    except Exception as e:
        print(f"Error processing {url}: {e}")

def process_articles():
    processed_articles = []

    # Progress bar setup
    with tqdm(total=len(article_urls), desc="Processing Articles", ncols=100) as pbar:
        for url in article_urls:
            scrape_article(url, processed_articles)
            pbar.update(1)

    # Final checkpoint after all articles are processed
    save_checkpoint(processed_articles)
    print(f"All articles processed. Final checkpoint saved.")

# Use threading to process articles in parallel
def thread_task(start_index, end_index, processed_articles):
    for url in article_urls[start_index:end_index]:
        scrape_article(url, processed_articles)

def main():
    # Split the articles into smaller chunks for multithreading
    num_threads = 35
    chunk_size = len(article_urls) // num_threads
    threads = []
    processed_articles = []

    for i in range(num_threads):
        start_index = i * chunk_size
        # Ensure the last thread processes any remaining articles
        end_index = (i + 1) * chunk_size if i != num_threads - 1 else len(article_urls)
        thread = threading.Thread(target=thread_task, args=(start_index, end_index, processed_articles))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Final checkpoint update after all threads finish
    save_checkpoint(processed_articles)
    print(f"All articles processed. Final checkpoint saved.")

if __name__ == "__main__":
    main()
