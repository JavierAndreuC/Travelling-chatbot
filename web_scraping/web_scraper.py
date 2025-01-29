### Main web scraper script to get initial main event info

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import time

# --- Selenium imports ---
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By  

# Set up web scraper agent
class TomorrowlandScraper:
    def __init__(self, output_dir='../chatbot-backend/chatbot/scraped_data'):
        self.output_dir = output_dir
        self.base_url = 'https://www.tomorrowland.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make sure the path exists to store the data that is being retrieved
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def get_event_cards(self):
        """Extract all event cards and their information from the calendar page"""
        try:
            options = Options()
            options.headless = True  # run in headless mode
            driver = webdriver.Chrome(options=options)
            
            driver.get(f"{self.base_url}home/events/")
            
            # Deal with the cookie popup
            time.sleep(2)  # let cookie popup appear
            try:
                accept_button = driver.find_element(By.XPATH, "//button[contains(text(),'Accept')]")
                accept_button.click()
                time.sleep(2)  # make sure cookie popup is gone
            except NoSuchElementException:
                pass  # Continue if no popup

            # Wait for the page content to load
            time.sleep(3)
            
            page_source = driver.page_source
            driver.quit()

            # Initialise parser
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find the event cards
            event_cards = soup.find_all('div', class_='EventCardLarge_eventCard__ZlYSq')
            
            # Extract and store data for each of the event cards
            events_data = []
            for card in event_cards:
                content_div = card.find('div', class_='EventCardLarge_content__ylgrw') # Get content section
                if content_div: # Get relevant data from the content section
                    title = content_div.find('h3').get_text().strip() if content_div.find('h3') else None
                    date_div = content_div.find('div', class_='EventCardLarge_date__07NO0')
                    date = date_div.find('p').get_text().strip() if date_div and date_div.find('p') else None
                    location_div = content_div.find('div', class_='EventCardLarge_location__D3ipV')
                    location = location_div.find('p').get_text().strip() if location_div and location_div.find('p') else None
                    links_div = content_div.find('div', class_='EventCardLarge_links__Xu8_7')
                    
                    # Add any extra links that can link to relevant pages
                    additional_links = {}
                    if links_div:
                        for link in links_div.find_all('a'):
                            link_text = link.get_text().strip().lower()
                            link_url = link.get('href')
                            additional_links[link_text] = link_url
                    
                    # Retrieve the URL from the 'info' key if it exists
                    info_url = additional_links.get('info')

                    # Remove the 'info' key so it's not in 'additional_links' anymore
                    additional_links.pop('info', None)

                    # Make a json record for each event and store it
                    events_data.append({
                        'title': title,
                        'url': info_url,
                        'date': date,
                        'location': location,
                        'additional_links': additional_links,  # 'info' has now been removed
                        'scraped_at': datetime.now().isoformat()
                    })
            
            return events_data
        except Exception as e:
            print(f"Error extracting event cards: {str(e)}")
            return []

    def save_to_file(self, data, filename):
        """Save scraped data to a file"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {filepath}")

    def run_scraper(self):
        """Run the scraping process"""
        print("Extracting event card information...")
        events_data = self.get_event_cards()
        
        if events_data:
            print(f"Found {len(events_data)} events")
            self.save_to_file(events_data, 'event_cards.json')
        else:
            print("No events found")

if __name__ == "__main__":
    scraper = TomorrowlandScraper()
    scraper.run_scraper()