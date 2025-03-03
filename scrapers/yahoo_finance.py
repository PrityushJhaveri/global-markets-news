# scrapers/yahoo_finance.py
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import random

class YahooFinanceScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        # Map Yahoo Finance regional pages to our country codes
        self.country_pages = {
            'us': 'https://finance.yahoo.com/news/',
            'uk': 'https://uk.finance.yahoo.com/news/',
            'ca': 'https://ca.finance.yahoo.com/news/',
            'au': 'https://au.finance.yahoo.com/news/',
            'in': 'https://in.finance.yahoo.com/news/',
            'sg': 'https://sg.finance.yahoo.com/news/',
            'hk': 'https://hk.finance.yahoo.com/news/',
            'jp': 'https://finance.yahoo.co.jp/news/',
        }
        # For other countries we'll use categories and keywords

    def get_country_news(self, country_code):
        """Get news for a specific country."""
        if country_code in self.country_pages:
            url = self.country_pages[country_code]
        else:
            # Default to global news and filter later
            url = 'https://finance.yahoo.com/news/'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            
            # Yahoo Finance structure (might need updates if they change their layout)
            articles = soup.find_all('div', {'class': 'Ov(h)'})
            
            for article in articles:
                # Extract data from each article
                headline_tag = article.find('h3')
                if not headline_tag:
                    continue
                    
                headline = headline_tag.text.strip()
                
                # Get link
                link_tag = article.find('a')
                link = f"https://finance.yahoo.com{link_tag['href']}" if link_tag else ""
                
                # Get source and time
                source_tag = article.find('div', {'class': 'C(#959595)'})
                source_text = source_tag.text if source_tag else ""
                
                # Extract source and time from combined text
                source = "Yahoo Finance"
                publish_time = "Today"
                
                if "·" in source_text:
                    parts = source_text.split("·")
                    source = parts[0].strip()
                    publish_time = parts[1].strip() if len(parts) > 1 else "Today"
                
                # Simple classification by keywords
                asset_class = self._classify_asset_class(headline)
                
                # If not using a country-specific page, try to determine country from content
                if country_code not in self.country_pages:
                    detected_country = self._detect_country(headline)
                    if detected_country and detected_country != country_code:
                        continue  # Skip if not relevant to requested country
                
                news_items.append({
                    'headline': headline,
                    'link': link,
                    'source': source,
                    'time': publish_time,
                    'country': country_code,
                    'asset_class': asset_class
                })
            
            # Add a delay to be respectful
            time.sleep(random.uniform(1.0, 2.0))
            return news_items
            
        except Exception as e:
            print(f"Error scraping Yahoo Finance ({country_code}): {e}")
            return []
    
    def _classify_asset_class(self, text):
        """Simple keyword-based classification for asset classes."""
        text = text.lower()
        
        if any(word in text for word in ['stock', 'share', 'equity', 'nasdaq', 'dow', 's&p']):
            return 'stocks'
        elif any(word in text for word in ['bond', 'treasury', 'yield', 'debt']):
            return 'bonds'
        elif any(word in text for word in ['currency', 'forex', 'dollar', 'euro', 'yen', 'pound']):
            return 'currencies'
        elif any(word in text for word in ['gold', 'oil', 'commodity', 'crude', 'natural gas']):
            return 'commodities'
        elif any(word in text for word in ['bitcoin', 'crypto', 'ethereum', 'token']):
            return 'crypto'
        else:
            return 'general'
    
    def _detect_country(self, text):
        """Simple keyword-based country detection."""
        text = text.lower()
        
        country_keywords = {
            'us': ['us', 'united states', 'america', 'washington', 'new york', 'fed', 'nasdaq', 'dow'],
            'uk': ['uk', 'britain', 'england', 'london', 'british'],
            'jp': ['japan', 'japanese', 'tokyo', 'yen', 'nikkei'],
            'cn': ['china', 'chinese', 'beijing', 'shanghai'],
            'eu': ['europe', 'european', 'euro', 'ecb', 'brussels'],
            'de': ['germany', 'german', 'berlin', 'frankfurt'],
            'fr': ['france', 'french', 'paris'],
            'in': ['india', 'indian', 'mumbai', 'delhi'],
            # Add more countries as needed
        }
        
        for country, keywords in country_keywords.items():
            if any(keyword in text for keyword in keywords):
                return country
        
        return None