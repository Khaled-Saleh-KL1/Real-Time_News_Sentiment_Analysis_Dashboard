from pymongo import MongoClient
import logging

def create_mongo_connection(db_name):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client[db_name]
        
        # Check if the unique index on 'url' already exists
        index_info = db["raw_news"].index_information()
        if "url_1" not in index_info:
            db["raw_news"].create_index("url", unique=True)
            logging.info("Unique index created on 'url' field in 'raw_news' collection")
        else:
            logging.info("Unique index on 'url' field already exists")
        
        return db
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        raise