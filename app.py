from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from kafka import KafkaProducer, KafkaConsumer
import json
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from user import User
from forms import LoginForm, RegisterForm  # Import the form classes


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Kafka setup
producer = KafkaProducer(bootstrap_servers='kafka:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                         api_version=(0,11,5))

# consumer = KafkaConsumer('purchases',
#                          bootstrap_servers='kafka:9092',
#                          value_deserializer=lambda m: json.loads(m.decode('utf-8')),
#                          api_version=(0,11,5))

# MongoDB setup
client = MongoClient('mongodb://osher:123456@mongo:27017/') # mongodb://localhost:27017/
db = client['mydatabase']
products_col = db['products']
purchases_col = db['purchases']

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(user_id)


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if current_user.is_admin:
        return redirect(url_for('admin'))  # Redirect to admin view if user is admin
    else:
        products = list(products_col.find())
        return render_template('index.html', products=products)
    # products = list(products_col.find())
    # return render_template('index.html', products=products)


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


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        # Since you are using MongoDB, use your User class methods to find the user
        user = User.find_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            error = "Invalid email or password."
    return render_template('login.html', form=form, error=error)


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Logic to handle registration
        # For example, create a new User, set password, and save to MongoDB
        user = User(email=form.email.data)
        user.set_password(form.password.data)  # Hash the password
        user.save_to_db()  # Save the user to the MongoDB

        # After registration, you might want to log the user in or redirect to the login page
        # login_user(user)
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin route
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    products = list(products_col.find())

    if request.method == 'POST':
        if 'add_product' in request.form:
            # Logic to add a product
            name = request.form.get('name')
            price = request.form.get('price')
            image_url = request.form.get('image_url')
            products_col.insert_one({'name': name, 'price': price, 'image_url': image_url})

        elif 'remove_product' in request.form:
            # Logic to remove a product
            product_id = request.form.get('product_id')
            products_col.delete_one({'_id': product_id})

        return redirect(url_for('admin'))

    return render_template('admin.html', products=products)


if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")
