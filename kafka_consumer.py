from kafka import KafkaConsumer
import json
from pymongo import MongoClient

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
purchases_col = db['purchases']

# Kafka consumer setup
consumer = KafkaConsumer('purchases',
                         bootstrap_servers='localhost:9092',
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))

for message in consumer:
    # Process each message
    purchase_data = message.value
    # Save to MongoDB
    purchases_col.insert_one(purchase_data)
