from flask import Flask, render_template
from pymongo import MongoClient
import logging

app = Flask(__name__)

@app.route('/')
def index():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["classified_data_db"]
        collection = db["classified_news"]
        
        # Retrieve articles with sentiment data
        news = list(collection.find().sort("date", -1).limit(100))
        
        # Ensure each article has a valid 'sentiment' field
        for article in news:
            if 'sentiment' not in article or not isinstance(article['sentiment'], dict):
                article['sentiment'] = {'Pos': 0, 'Neu': 0, 'Neg': 0}  # Default sentiment data
        
        return render_template('index.html', news=news)
    except Exception as e:
        logging.error(f"Error fetching data for dashboard: {e}")
        return render_template('error.html', message="An error occurred while fetching data.")

def start_dashboard():
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        logging.error(f"Error starting dashboard: {e}")