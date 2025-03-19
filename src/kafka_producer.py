from kafka import KafkaProducer
import json
import logging

class KafkaProducerClass:
    def __init__(self, topic, bootstrap_servers='localhost:9092'):
        self.topic = topic
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            logging.error(f"Error initializing Kafka producer: {e}")
            raise

    def send_data(self, data):
        try:
            self.producer.send(self.topic, value=data)
            self.producer.flush()
            logging.info(f"✅ Data sent to Kafka topic '{self.topic}'")
        except Exception as e:
            logging.error(f"Error sending data to Kafka: {e}")