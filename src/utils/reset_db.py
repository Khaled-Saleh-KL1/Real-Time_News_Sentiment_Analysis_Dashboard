from pymongo import MongoClient
import logging

def reset_database(db_name):
    """
    Deletes the specified MongoDB database.
    
    Args:
        db_name (str): The name of the database to delete.
    """
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        
        # Drop the database
        client.drop_database(db_name)
        logging.info(f"✅ Database '{db_name}' deleted successfully.")
    except Exception as e:
        logging.error(f"❌ Error deleting database '{db_name}': {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Specify the database name to delete
    reset_database("raw_data_db")
