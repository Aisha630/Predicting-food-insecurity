import json
import requests
from bs4 import BeautifulSoup
import re

def extract_article_info(url):
    """
    Fetches the HTML content of the given URL and extracts:
      - Heading from the <h1> element within div.news_article
      - Subheading from the <h2> element within div.news_article
      - Article content from all nested <p> tags (assumed to hold the Urdu or mixed content)
    
    Returns a dictionary with the extracted data.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error accessing the URL {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    news_article_div = soup.find("div", class_="news_article")
    if not news_article_div:
        print(f"The news_article div was not found on {url}")
        return None

    heading_tag = news_article_div.find("h1")
    subheading_tag = news_article_div.find("h2")
    heading_text = heading_tag.get_text(strip=True) if heading_tag else "No heading found"
    subheading_text = subheading_tag.get_text(strip=True) if subheading_tag else "No subheading found"

    paragraphs = news_article_div.find_all("p")
    content_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    return {
        "heading": heading_text,
        "subheading": subheading_text,
        "content": content_text
    }

def extract_date_from_url(url):
    """
    Extracts the date from a URL.
    The URL is expected in the format:
    https://www.urdupoint.com/daily/livenews/YYYY-MM-DD/news-<7digit>.html
    """
    pattern = r"/daily/livenews/(\d{4}-\d{2}-\d{2})/"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return "Unknown Date"

def main():
    # Read filtered URLs from the text file (one URL per line)
    input_file = "2-years-links.txt"
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    except IOError as e:
        print(f"Error reading {input_file}: {e}")
        return

    articles = []

    for url in urls:
        print(f"Processing: {url}")
        article_info = extract_article_info(url)
        if article_info:
            date_str = extract_date_from_url(url)
            article_entry = {
                "date": date_str,
                "title": article_info.get("heading", ""),
                "content": article_info.get("content", "")
            }
            articles.append(article_entry)
        else:
            print(f"Skipping URL due to extraction failure: {url}")

    # Save all articles to a JSON file
    output_file = "articles.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        print(f"\nSaved {len(articles)} articles to '{output_file}'")
    except IOError as e:
        print(f"Error writing to file {output_file}: {e}")

if __name__ == "__main__":
    main()
