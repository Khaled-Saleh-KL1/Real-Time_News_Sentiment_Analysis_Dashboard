## Financial News Sentiment Analysis Dashboard

### Project Overview
This project is a real-time financial news aggregator and sentiment analysis system. It scrapes financial news articles from NewsAPI, analyzes their sentiment using a pre-trained finance-specific FineBERT model, and presents the results in a web dashboard. The system uses Kafka for message streaming between components, MongoDB for data storage, and Flask for the web interface.

### Features
- Real-time News Scraping: Collects financial news articles from NewsAPI at regular intervals.
- Duplicate Detection: Filters out duplicate articles based on URL and title
- Sentiment Analysis: Uses a finance-specific BERT model to analyze the sentiment of news headlines
- Web Dashboard: Presents the analyzed news with sentiment indicators (Positive, Neutral, Negative)
- Distributed Architecture: Uses Kafka for message streaming between components

### System Architecture
```
                ┌───────────┐
                │  NewsAPI  │
                └─────┬─────┘
                      │
                      ▼
┌─────────────┐    ┌──────────────┐
│  MongoDB    │◄───┤    Scraper   │
│ (raw_data)  │    └───────┬──────┘
└─────────────┘            │
                           ▼
                    ┌─────────────┐
                    │   Kafka     │
                    │  Producer   │
                    └──────┬──────┘
                           │
                           ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  MongoDB    │◄───┤    Kafka    │◄───┤  Sentiment  │
│(classified) │    │  Consumer   │    │  Analyzer   │
└──────┬──────┘    └─────────────┘    └─────────────┘
       │
        ▼
┌─────────────┐
│    Flask    │
│  Dashboard  │
└─────────────┘
```

### Requirements
- Python 3.8+
- MongoDB 4.4+
- Apache Kafka 2.6+
- NewsAPI account and API key

### Dependencies
flask==2.0.1
kafka-python==2.0.6
pymongo==4.0.1
requests==2.26.0
schedule==1.1.0
torch==1.10.0
transformers==4.11.3
tensorflow>=2.0.0

### Installation
1. Clone the repository:
```
git clone https://github.com/Khaled-Saleh-KL1/Real-Time_News_Sentiment_Analysis_Dashboard.git
cd Real-Time_News_Sentiment_Analysis_Dashboard
```

2. Start MongoDB Service
```
systemctl enable mongod.service
```

3. Start Kafka
```
# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# start Server
bin/kafka-server-start.sh config/server.properties

# Create a topic
bin/kafka-topics.sh --create --topic scraped_data --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### Usage
Run the main application
```
python3 main.py
```
This will:
1. Start scraping financial news at regular intervals (every 60 minutes)
2. Process and analyze the sentiment of the news using the BERT model
3. Store results in MongoDB
4. Launch a web dashboard at http://localhost:5000 or http://127.0.0.1:5000

### Components
- **main.py**: Orchestrates the entire system
- **scraper.py**: Fetches financial news from NewsAPI
- **kafka_producer.py**: Sends scraped news to Kafka
- **kafka_consumer.py**: Consumes news from Kafka for processing
- **transformer.py**: Analyzes sentiment using a pre-trained BERT model
- **dashboard.py**: Displays the news and their sentiment in a web interface
- **utils/db.py**: Handles database connections and operations
- **utils/reset_db.py**: To delete the database

### Authors
Khaled Saleh

[Mohanad Assaf](https://github.com/kabuto1012)
