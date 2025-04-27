import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

driver_path = ChromeDriverManager().install()
driver = webdriver.Chrome(service=ChromeService(executable_path=driver_path), options=options)
wait = WebDriverWait(driver, 30)

with open("districts.csv", "r", newline='', encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        district = row["district"].strip()
        url = row["url"].strip()
        print("\n--- Processing district: '{}' with URL: {} ---".format(district, url))

        driver.get(url)
        time.sleep(3)

        article_links = set()
        selector = "a[href*='/pakistan/news/{}']".format(district.lower())
        
        # Step 1: Collect initial articles
        try:
            articles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            for article in articles:
                href = article.get_attribute("href")
                if href:
                    article_links.add(href)
            print("Initially found {} article links for '{}'.".format(len(article_links), district))
        except Exception as e:
            print("Error collecting initial articles for '{}': {}".format(district, e))
            continue  # Skip to the next district if initial scraping fails.
        
        # Step 2: Click "Load More" up to a maximum number of times
        max_clicks = 50
        for i in range(1, max_clicks + 1):
            try:
                # Locate the "Load More"
                load_more_span = wait.until(EC.presence_of_element_located((By.ID, "btn_load_more")))
                
                # Scroll
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_span)
                time.sleep(1)

                try:
                    load_more_span.click()
                    print("Iteration {} for '{}': Clicked 'Load More' (Selenium click).".format(i, district))
                except Exception as click_e:
                    print("Iteration {} for '{}': Selenium click failed: {}. Trying JS click...".format(i, district, click_e))
                    driver.execute_script("arguments[0].click();", load_more_span)
                    print("Iteration {} for '{}': Clicked 'Load More' using JS.".format(i, district))
                
                time.sleep(3)
                
                # Re-collect article links after clicking "Load More"
                new_articles = driver.find_elements(By.CSS_SELECTOR, selector)
                before_count = len(article_links)
                for art in new_articles:
                    link = art.get_attribute("href")
                    if link:
                        article_links.add(link)
                after_count = len(article_links)
                print("Iteration {} for '{}': Links increased from {} to {}.".format(i, district, before_count, after_count))
                
                # If no new articles were loaded, break out of the loop.
                if after_count == before_count:
                    print("Iteration {} for '{}': No new articles loaded. Breaking loop.".format(i, district))
                    break

            except Exception as e:
                print("Iteration {} for '{}': Couldn't find or click 'Load More': {}".format(i, district, e))
                break
        
        # Step 3: Save the collected article links to an output CSV file
        # output file name is based on the district value.
        output_csv = "{}_article_links.csv".format(district.replace(" ", "_"))
        with open(output_csv, "w", newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Article Links"])
            for link in article_links:
                writer.writerow([link])
        print("For '{}', saved {} article links to '{}'.".format(district, len(article_links), output_csv))

driver.quit()
print("\nAll done. Browser closed.")