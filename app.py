from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from kafka import KafkaProducer, KafkaConsumer
import json

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
    products = list(products_col.find())
    return render_template('index.html', products=products)


@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image_url = request.form.get('image_url')

        products_col.insert_one({'name': name, 'price': price, 'image_url': image_url})

        return redirect(url_for('index'))

    return render_template('add_product.html')


@app.route('/buy', methods=['POST'])
def buy():
    product_id = request.form.get('product_id')
    producer.send('purchases', {'product_id': product_id})
    return jsonify({'status': 'success'})


@app.route('/purchased')
def purchased():
    bought_items = list(purchases_col.find())
    return render_template('purchased.html', items=bought_items)


if __name__ == '__main__':
    app.run(debug=True, port=8000, host="127.0.0.1")
