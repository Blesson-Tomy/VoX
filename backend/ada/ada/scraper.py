import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

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
            
            print(f"Scraping URL: {self.url}")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            
            articles = soup.find_all('div', class_='views-row')
            bills_data = []
            
            print(f"Found {len(articles)} total articles")
            
            for article in articles:
                
                title = article.find('h3', class_='cate')
                status = article.find('span', class_='status-pending')
                
                
                if title and status and status.text.strip() == 'In Committee':
                    title_text = title.text.strip()
                    
                    
                    summary_div = article.find('div', class_='field-content')
                    summary_text = summary_div.text.strip() if summary_div else "No summary available"
                    
                    
                    article_link = title.find_parent('a')
                    article_url = f"https://prsindia.org{article_link['href']}" if article_link else None
                    
                    bill_data = {
                        'title': title_text,
                        'summary': summary_text, 
                        'status': 'pending',
                        'url': article_url,
                        'scraped_at': ''.join(re.findall(r'\d', title_text))
                    }
                    
                    bills_data.append(bill_data)
                    print(f"Added pending bill: {title_text}")
                else:
                    skip_reason = "Missing title" if not title else "Not pending"
                    print(skip_reason)
                    
        
            print(f"Successfully scraped {len(bills_data)} pending bills")
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
            
      
            content_div = soup.find('div', {'class': 'field-content'})
            
            if content_div:
                return (f"Article URL: {url}\n\n"
                       f"Content: {content_div.text.strip()}\n"
                       f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}")
            return "Content not available"
            
        except Exception as e:
            print(f"Error getting article details: {str(e)}")
            return "Error retrieving content"