from kafka import KafkaConsumer
import json
from pymongo import MongoClient
from transformer import finance_prop
import datetime
import logging
import hashlib
from pymongo.errors import DuplicateKeyError

class KafkaConsumerClass:
    def __init__(self, topic, bootstrap_servers='localhost:9092'):
        try:
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='news_group'
            )
            self.classifier = finance_prop()
            self.client = MongoClient("mongodb://localhost:27017/")
            self.db = self.client["classified_data_db"]
            self.collection = self.db["classified_news"]
            
            # Clean up duplicates before adding a unique index
            self._clean_duplicates()
            
            # Check if indices exist before creating them
            self._ensure_indices()
            
        except Exception as e:
            logging.error(f"Error initializing Kafka consumer: {e}")
            raise

    def _clean_duplicates(self):
        """Remove duplicate articles based on URL before creating unique index"""
        try:
            # Find all URLs in the collection
            urls = self.collection.distinct("url")
            
            # For each URL, keep only the latest document
            for url in urls:
                if url:  # Skip None/empty URLs
                    # Find all documents with this URL
                    docs = list(self.collection.find({"url": url}).sort("date", -1))
                    
                    if len(docs) > 1:
                        # Keep the first one (newest), delete the rest
                        for doc in docs[1:]:
                            self.collection.delete_one({"_id": doc["_id"]})
                        logging.info(f"Cleaned up {len(docs)-1} duplicates for URL: {url}")
            
            logging.info("Duplicate cleanup completed successfully")
        except Exception as e:
            logging.error(f"Error cleaning duplicates: {e}")

    def _ensure_indices(self):
        """Create necessary indices if they don't exist"""
        try:
            # Get existing indices
            index_info = self.collection.index_information()
            
            # Create date index if it doesn't exist
            if "date_-1" not in index_info:
                self.collection.create_index([("date", -1)])
                logging.info("Created index on 'date' field")
            
            # Create title index if it doesn't exist
            if "title_1" not in index_info:
                self.collection.create_index("title")
                logging.info("Created index on 'title' field")
            
            # Create unique URL index if it doesn't exist
            if "url_1" not in index_info:
                # Use sparse=True to allow documents without a URL field
                self.collection.create_index("url", unique=True, sparse=True)
                logging.info("Created unique index on 'url' field")
        except Exception as e:
            logging.error(f"Error creating indices: {e}")
            # Continue even if index creation fails - we'll handle duplicates in code

    def consume_data(self):
        for message in self.consumer:
            try:
                data = message.value
                
                # Skip if we already have this article (check by URL)
                if 'url' in data and data['url']:
                    existing = self.collection.find_one({'url': data['url']})
                    if existing:
                        logging.info(f"Skipping duplicate article: {data.get('title', data.get('url'))}")
                        continue
                
                # Generate a title hash for articles without URLs
                if 'title' in data:
                    title_hash = hashlib.md5(data['title'].encode()).hexdigest()
                    if not data.get('url') and self.collection.find_one({'title_hash': title_hash}):
                        logging.info(f"Skipping duplicate article by title hash: {data.get('title')}")
                        continue
                    data['title_hash'] = title_hash
                
                if self.classifier.is_finance_related(data['title']):
                    sentiment = self.classifier.get_sentiment([data['title']])[0]
                    if not isinstance(sentiment, dict) or not all(key in sentiment for key in ['Pos', 'Neu', 'Neg']):
                        logging.warning(f"Invalid sentiment data for article: {data['title']}")
                        continue  # Skip this article if sentiment data is invalid
                    
                    data['sentiment'] = sentiment
                    data['date'] = data.get('publishedAt', datetime.datetime.now(datetime.timezone.utc).isoformat())
                    
                    try:
                        # If URL exists, use it as the unique identifier
                        if 'url' in data and data['url']:
                            result = self.collection.update_one(
                                {'url': data['url']},
                                {'$set': data},
                                upsert=True
                            )
                        # Otherwise use title_hash
                        else:
                            result = self.collection.update_one(
                                {'title_hash': data['title_hash']},
                                {'$set': data},
                                upsert=True
                            )
                        
                        if result.modified_count > 0 or result.upserted_id:
                            logging.info(f"✅ Data classified and stored in MongoDB: {data['title']}")
                        else:
                            logging.info(f"Article already exists, no changes made: {data['title']}")
                            
                    except DuplicateKeyError:
                        logging.info(f"Skipped duplicate article during insert: {data.get('title')}")
                    except Exception as e:
                        logging.error(f"Error storing article in MongoDB: {e}")
            except Exception as e:
                logging.error(f"Error processing Kafka message: {e}")

    def close(self):
        """Close the Kafka consumer and MongoDB client."""
        try:
            self.consumer.close()
            self.client.close()
            logging.info("Kafka consumer and MongoDB client closed successfully.")
        except Exception as e:
            logging.error(f"Error closing resources: {e}")