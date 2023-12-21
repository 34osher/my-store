"""
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from kafka import KafkaProducer, KafkaConsumer
import json
"""
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)

# Kafka setup
producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

consumer = KafkaConsumer('purchases',
                         bootstrap_servers='localhost:9092',
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
products_col = db['products']
purchases_col = db['purchases']


@app.route('/')
def index():
    products = products_col.find()
    return render_template('index.html', products=products)


@app.route('/buy', methods=['POST'])
def buy():
    product_id = request.form.get('product_id')
    # Produce a message to Kafka
    producer.send('purchases', {'product_id': product_id})
    return jsonify({'status': 'success'})


@app.route('/purchased')
def purchased():
    bought_items = list(purchases_col.find())
    return render_template('purchased.html', items=bought_items)


if __name__ == '__main__':
    app.run(debug=True, port=8000, host="127.0.0.1")
