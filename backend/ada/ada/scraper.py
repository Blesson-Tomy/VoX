import requests
from bs4 import BeautifulSoup
from datetime import datetime

class BillScraper:
    def __init__(self):
        self.url = "https://prsindia.org/billtrack"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def scrape_bills(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            
            print(f"Scraping URL: {self.url}")  # Debug print
            print(f"Response status: {response.status_code}")  # Debug print
            
            soup = BeautifulSoup(response.text, 'html.parser')
            article_titles = soup.find_all('h3', class_='cate')
            
            print(f"Found {len(article_titles)} articles with h2.cate")  # Debug print
            
            
            if not article_titles:
                # If no articles found, print the HTML to debug
                print("HTML content:", soup.prettify()[:500])  # Print first 500 chars
            
            bills_data = []
            
            for title in article_titles:
                # Get the parent article link if it exists
                article_link = title.find_parent('a')
                article_url = f"https://prsindia.org{article_link['href']}" if article_link else None
                
                bill_data = {
                    'title': title.text.strip(),
                    'summary': self.get_article_details(article_url) if article_url else "Details not available"
                }
                bills_data.append(bill_data)
                print(f"Scraped: {bill_data['title']}")
            
            return bills_data
                    
        except Exception as e:
            print(f"Error scraping articles: {str(e)}")
            return []

    def get_article_details(self, url):
        """Get detailed content from the article page"""
        try:
            if not url:
                return "URL not available"
                
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find article content
            content_div = soup.find('div', {'class': 'field-content'})
            
            if content_div:
                return (f"Article URL: {url}\n\n"
                       f"Content: {content_div.text.strip()}\n"
                       f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}")
            return "Content not available"
            
        except Exception as e:
            print(f"Error getting article details: {str(e)}")
            return "Error retrieving content"