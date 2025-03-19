import requests
import datetime
from pymongo import MongoClient
import logging
import os

class NewsAPIScraper:
    def __init__(self):
        self.API_KEY = os.getenv("NEWS_API_KEY", "167d55dada81424699c3552a8b2f042d")
        self.url = "https://newsapi.org/v2/everything"
        try:
            self.client = MongoClient("mongodb://localhost:27017/")
            self.db = self.client["raw_data_db"]
            self.collection = self.db["raw_news"]
        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {e}")
            raise

    def processed_articles(self, articles):
        processed = []
        for article in articles:
            processed.append({
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", ""),
                "publishedAt": article.get("publishedAt", ""),
                "url": article.get("url", ""),
            })
        return processed

    def fetch_financial_news(self):
        # 1 days ago
        date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        params = {
            "q": "finance OR market OR economy OR revenue OR stock OR investment",
            "from": date,
            "sortBy": "publishedAt",
            "apiKey": self.API_KEY
        }
        
        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            
            # Log the response status and headers for debugging
            logging.info(f"NewsAPI response status: {response.status_code}")
            logging.info(f"NewsAPI rate limits: {response.headers.get('X-RateLimit-Remaining', 'N/A')}/{response.headers.get('X-RateLimit-Limit', 'N/A')}")
            
            articles = response.json().get("articles", [])
            logging.info(f"NewsAPI returned {len(articles)} raw articles")
            
            if not articles:
                logging.warning(f"NewsAPI response: {response.json()}")
            
            # Get existing URLs from the database
            existing_urls = set(doc["url"] for doc in self.collection.find({}, {"url": 1}))
            
            # Filter out duplicates based on URL and title hash
            seen_titles = set()
            unique_articles = []
            
            for article in articles:
                url = article.get("url", "")
                title = article.get("title", "").strip()
                
                # Skip if URL already exists in the database
                if url in existing_urls:
                    continue
                    
                # Skip if title is very similar to one we've already seen
                if title in seen_titles:
                    continue
                    
                seen_titles.add(title)
                
                # Ensure article has all required fields
                if all(k in article for k in ["title", "url", "source"]):
                    unique_articles.append(article)
            
            # Process the unique articles
            processed_articles = self.processed_articles(unique_articles)
            
            logging.info(f"Found {len(articles)} articles, filtered to {len(processed_articles)} unique new articles")
            return processed_articles
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching news: {e}")
            return []