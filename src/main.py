from scraper import NewsAPIScraper
from kafka_producer import KafkaProducerClass
from kafka_consumer import KafkaConsumerClass
from utils.db import create_mongo_connection
from dashboard import start_dashboard
import threading
import time
import schedule
import logging
from pymongo.errors import DuplicateKeyError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_and_process_news():
    """Fetch news and send to Kafka"""
    try:
        # Create MongoDB connections
        raw_data_db = create_mongo_connection('raw_data_db')
        raw_data_collection = raw_data_db['raw_news']

        # Initialize Kafka producer
        producer = KafkaProducerClass(topic='scraped_data')

        # Scrape data and send to Kafka
        newsapi_scraper = NewsAPIScraper()
        raw_data = newsapi_scraper.fetch_financial_news()
        
        logging.info(f"Fetched {len(raw_data)} new articles at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        for data in raw_data:
            try:
                # First check if this article already exists to avoid sending duplicates to Kafka
                if 'url' in data and raw_data_collection.count_documents({'url': data['url']}) > 0:
                    logging.info(f"Skipping existing article: {data['url']}")
                    continue
                
                # Send unique article to Kafka
                producer.send_data(data)
                
                # Store in raw data collection with upsert to avoid duplicates
                if 'url' in data and data['url']:
                    raw_data_collection.update_one(
                        {'url': data['url']}, 
                        {'$set': data}, 
                        upsert=True
                    )
                    logging.info(f"✅ Raw article stored in MongoDB: {data['title']}")
            except DuplicateKeyError:
                logging.warning(f"Duplicate article skipped: {data['url']}")
            except Exception as e:
                logging.error(f"Error processing article: {e}")
    except Exception as e:
        logging.error(f"Error in fetch_and_process_news: {e}")

def start_scheduler():
    """Start the scheduler for real-time data fetching"""
    # Run immediately on startup
    fetch_and_process_news()
    
    # Then schedule to run every 30 minutes
    schedule.every(30).minutes.do(fetch_and_process_news)
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    try:
        # Start Kafka consumer in a separate thread
        consumer = KafkaConsumerClass(topic='scraped_data')
        consumer_thread = threading.Thread(target=consumer.consume_data)
        consumer_thread.daemon = True  # Allow the thread to exit when the main program exits
        consumer_thread.start()
        
        # Start the scheduler in a separate thread
        scheduler_thread = threading.Thread(target=start_scheduler)
        scheduler_thread.daemon = True  # Allow the thread to exit when the main program exits
        scheduler_thread.start()
        
        # Start dashboard (this will block the main thread)
        start_dashboard()
    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()