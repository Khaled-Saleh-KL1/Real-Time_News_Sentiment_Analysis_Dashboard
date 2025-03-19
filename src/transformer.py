import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import logging

class finance_prop:
    def __init__(self):
        # self.MODEL_NAME = 'RashidNLP/Finance-Sentiment-Classification'
        # self.MODEL_NAME = 'ProsusAI/finbert'
        self.MODEL_NAME = 'yiyanghkust/finbert-tone'

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        try:
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_NAME, num_labels=3).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise

    def get_sentiment(self, sentences):
        try:
            vectors = self.tokenizer(sentences, padding=True, max_length=65, return_tensors='pt').to(self.device)
            outputs = self.bert_model(**vectors).logits
            probs = torch.nn.functional.softmax(outputs, dim=1)
            
            # Debugging: Print the raw output
            logging.info(f"Raw sentiment output: {outputs}")
            logging.info(f"Probabilities: {probs}")
            
            return [{'Pos': round(prob[0].item(), 3), 'Neu': round(prob[1].item(), 3), 'Neg': round(prob[2].item(), 3)} for prob in probs]
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {e}")
            return []

    def is_finance_related(self, text):
        finance_keywords = ["stock", "market", "finance", "investment", "economy", "revenue", "profit", "loss"]
        return any(keyword in text.lower() for keyword in finance_keywords)