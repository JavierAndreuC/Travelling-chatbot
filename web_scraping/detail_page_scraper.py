import json
import time
import re

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

class TomorrowlandDetailScraper:
    def __init__(self):
        """Initialize a headless Chrome browser for detail scraping."""
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
    
    def accept_cookies_if_present(self):
        """Try to click any 'Accept cookies' popup or close any other popup that might appear. If not present, ignore."""
        time.sleep(2)  # let the popup appear if it exists
        try:
            accept_button = self.driver.find_element(By.XPATH, "//button[contains(text(),'Accept')]")
            accept_button.click()
            time.sleep(1.5)  # let it disappear
        except NoSuchElementException:
            pass  # No popup found, carry on

        # Check for "close" button if any extra modal might appear
        try:
            close_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label,'Close')]")
            close_button.click()
        except NoSuchElementException:
            pass

    def extract_text_from_url(self, url):
        """Go to the URL with Selenium, accept cookies if needed,
           extract all text from the page, then check for 'Timetable/Lineup' link
           and if found, open it and extract that text too."""
        self.driver.get(url)
        
        # Handle pop ups
        self.accept_cookies_if_present()

        # Parse the main page
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        main_text = soup.get_text(separator=" ", strip=True)

        # --- Look for a link that might say Timetable, Lineup, or Line-up ---
        link_pattern = re.compile(r"(timetable|line[\-\s]?up)", re.IGNORECASE)

        # Find all <a> tags that have text matching the pattern
        possible_links = soup.find_all("a", string=link_pattern)
        
        # Navigate to first link if found 
        if possible_links:
            link = possible_links[0]
            href = link.get("href", "")

            if href:
                # Make full url if href was relative (e.g., /timetable)
                full_link = self._make_absolute_url(url, href)

                # Open link
                print(f"Found a Timetable/Lineup link: {full_link}")
                self.driver.get(full_link)
                self.accept_cookies_if_present()

                # Parse page
                sub_page_source = self.driver.page_source
                sub_soup = BeautifulSoup(sub_page_source, "html.parser")
                sub_text = sub_soup.get_text(separator=" ", strip=True)

                # Append lineup text to the main page text
                main_text += "\n\n" + sub_text

        return main_text

    def _make_absolute_url(self, base_url, link_href):
        """Utility to build an absolute URL if link_href is relative."""
        # If link_href is already absolute (e.g., starts with http:// or https://),
        # just return it directly. Otherwise, join with the base domain.
        if link_href.startswith("http://") or link_href.startswith("https://"):
            return link_href
        else:
            # Try to combine with base
            from urllib.parse import urljoin
            return urljoin(base_url, link_href)

    def close(self):
        """Close the Selenium driver."""
        self.driver.quit()


def main():
    # Load previously scraped event_cards.json
    with open("../chatbot-backend/chatbot/scraped_data/event_cards.json", "r", encoding="utf-8") as f:
        events_data = json.load(f)

    # Create instance of our detail scraper
    detail_scraper = TomorrowlandDetailScraper()

    # For each event visit the 'url' and extract text
    for event in events_data:
        if not event.get("url"):
            continue  # skip if no URL

        print(f"Scraping detail text from: {event['title']} - {event['url']}")
        try:
            page_text = detail_scraper.extract_text_from_url(event["url"])
            event["page_text"] = page_text
        except Exception as e:
            print(f"Error scraping {event['url']}: {str(e)}")
            event["page_text"] = ""

    # Close the browser
    detail_scraper.close()

    # Save updated text
    with open("../chatbot-backend/chatbot/scraped_data/event_cards_with_text.json", "w", encoding="utf-8") as f:
        json.dump(events_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()