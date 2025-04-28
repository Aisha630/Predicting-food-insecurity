import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta

# Function to fetch articles from the given URL
def fetch_articles(url, date):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        # Loop through each article container
        for item in soup.find_all('div', class_='grid grid-cols-12 gap-2'):
            # Extract title and link
            title_tag = item.find('h2', class_='story__title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.find('a')['href']

                # Extract excerpt if available
                excerpt_tag = item.find('div', class_='story__excerpt')
                excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else 'No excerpt'

                # Extract image URL if available
                image_tag = item.find('img')
                image_url = image_tag['src'] if image_tag else 'No image'

                # Store the article information
                articles.append({
                    'title': title,
                    'link': link,
                    'date': date
                })
        return articles
    else:
        print(f"Failed to retrieve {url}")
        return []

# Function to generate URLs from 1 Jan 2023 to 10 Apr 2025
def generate_urls():
    base_url = 'https://www.dawnnews.tv/pakistan/'
    start_date = datetime.strptime('2023-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2025-04-10', '%Y-%m-%d')
    
    urls = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        urls.append(base_url + date_str + '/')
        current_date += timedelta(days=1)
    return urls

# Function to save articles to CSV
def save_to_csv(articles, filename='dawn_articles.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'link', 'date'])
        writer.writeheader()
        for article in articles:
            writer.writerow(article)
    print(f"Articles saved to {filename}")

# Main function to scrape articles and save them
def main():
    urls = generate_urls()
    all_articles = []
    for url in urls:
        date = url.split('/')[-2]  # Extract date from the URL (e.g., '2025-04-07')
        print(f"Fetching articles from {url}")
        articles = fetch_articles(url, date)
        if articles:
            all_articles.extend(articles)
    
    if all_articles:
        save_to_csv(all_articles)
    else:
        print("No articles found.")

if __name__ == '__main__':
    main()
