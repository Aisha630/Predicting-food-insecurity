import os
import csv
import json
import requests
from bs4 import BeautifulSoup
import re

def convert_urdu_date(date_str):
    """
    Converts an Urdu date string like "اتوار16فروری202517:00" into "yyyy-mm-dd".

    The expected format is:
      - Urdu day-of-week (ignored)
      - Day (1 or 2 digits)
      - Month name in Urdu (e.g., "فروری")
      - 4-digit Year
      - Time (ignored)

    Returns a string in "yyyy-mm-dd" format, or None if parsing fails.
    """
    # Mapping of Urdu month names to two-digit month numbers.
    urdu_months = {
        "جنوری": "01",
        "فروری": "02",
        "مارچ": "03",
        "اپریل": "04",
        "مئی": "05",
        "جون": "06",
        "جولائی": "07",
        "اگست": "08",
        "ستمبر": "09",
        "اکتوبر": "10",
        "نومبر": "11",
        "دسمبر": "12"
    }
    
    # Regular expression to extract the day, month, and year.
    # This pattern captures:
    #   - weekday: one or more non-digit characters at the start (ignored)
    #   - day: 1 or 2 digits
    #   - month: one or more non-digit characters (the month name)
    #   - year: exactly 4 digits
    pattern = r"^(?P<weekday>[^\d]+)(?P<day>\d{1,2})(?P<month>[^\d]+)(?P<year>\d{4})"
    match = re.match(pattern, date_str)
    
    if not match:
        print("Date string did not match expected format.")
        return None

    day = match.group("day").strip()
    month_name = match.group("month").strip()
    year = match.group("year").strip()

    month_number = urdu_months.get(month_name)
    if not month_number:
        print(f"Unrecognized month name: {month_name}")
        return None
    
    day = day.zfill(2)
    
    formatted_date = f"{year}-{month_number}-{day}"
    return formatted_date


def extract_article_info(url):
    """
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
    date = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    txt_banner_div = soup.find("div", class_="detail_txt urdu fs17 lh34 aj rtl")
    content_text = txt_banner_div.get_text(strip=True) if txt_banner_div else "No content found"


    return {
        "heading": heading_text,
        "subheading": subheading_text,
        "date": date,
        "content": content_text
    }

def extract_identifier_from_url(url):
    """
    Extracts the 7-digit article identifier from the URL which can contain either
    'national-news' or 'important-news'. 

    Example URL: 
      https://www.urdupoint.com/pakistan/news/<district>/(national-news|important-news)/live-news-<7_digits>.html

    Returns the identifier as a string if found, or 'Unknown_ID' otherwise.
    """
    pattern = r"(?:national-news|important-news)/live-news-(\d{7})\.html"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return "Unknown_ID"

def process_csv_file(csv_file):
    """Processes a single CSV file and returns a list of article entries."""
    district = os.path.basename(csv_file).replace("_article_links.csv", "")
    urls = []
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("Article Links", "").strip()
                if url:
                    urls.append(url)
    except IOError as e:
        print(f"Error reading {csv_file}: {e}")
        return []

    articles = []

    for url in urls:
        print(f"Processing [{district}]: {url}")
        article_info = extract_article_info(url)
        if article_info:
            article_entry = {

                "date":  convert_urdu_date(article_info.get("date", "")),
                "title": article_info.get("heading", ""),
                "content": article_info.get("content", "")
            }
            articles.append(article_entry)

        else:
            print(f"Skipping URL due to extraction failure: {url}")

    return district, articles

def main():
    csv_folder = "district_links"
    output_folder = "district-articles"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    if not os.path.exists(csv_folder):
        print(f"Folder not found: {csv_folder}")
        return

    for filename in os.listdir(csv_folder):
        if filename.endswith("_article_links.csv"):
            csv_file = os.path.join(csv_folder, filename)
            district, articles = process_csv_file(csv_file)
            if articles:
                output_file = os.path.join(output_folder, f"{district}_articles.json")
                try:
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(articles, f, ensure_ascii=False, indent=4)
                    print(f"\nSaved {len(articles)} articles for district '{district}' to '{output_file}'")
                except IOError as e:
                    print(f"Error writing to file {output_file}: {e}")
            else:
                print(f"No articles extracted for district '{district}'.")


if __name__ == "__main__":
    main()
