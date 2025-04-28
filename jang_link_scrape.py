import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor

# Define the start and end dates
start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 4, 10)

# Base URL for the national section archive
base_url = "https://jang.com.pk/category/today-newspaper-archive"

# Headers to mimic a browser visit
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

# List to store extracted article links
article_links = []

# Function to process a single date
def process_date(current_date):
    date_str = current_date.strftime("%Y-%m-%d")
    archive_url = f"{base_url}/{date_str}"

    try:
        response = requests.get(archive_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # Find all article links in the national section
            articles = soup.find_all("a", href=True)
            day_links = []
            for article in articles:
                href = article['href']
                # Filter links that belong to the national news section
                if "/news/" in href and href.startswith("https://jang.com.pk/news/"):
                    day_links.append(href)
            print(f"Processed {date_str}: Found {len(day_links)} articles.")
            return day_links
        else:
            print(f"Failed to retrieve {date_str}: Status code {response.status_code}")
    except Exception as e:
        print(f"Error processing {date_str}: {e}")
        return []

# Generate a list of dates to process
dates_to_process = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

# Use ThreadPoolExecutor to process dates concurrently
with ThreadPoolExecutor(max_workers=5) as executor:
    # Process dates and collect results
    results = list(executor.map(process_date, dates_to_process))

# Flatten the list of lists and remove duplicates
article_links = [link for sublist in results for link in sublist]
unique_links = list(set(article_links))

# Save the links to a file
with open("jang_national_articles.txt", "w", encoding="utf-8") as file:
    for link in unique_links:
        file.write(f"{link}\n")

print(f"Extraction complete. Total unique articles found: {len(unique_links)}")
