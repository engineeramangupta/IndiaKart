from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Load product data
with open('products.json') as f:
    products = json.load(f)

# Simulated user data storage
users = {}

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/home')
def home():
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('query', '')
    filtered_products = [p for p in products if query.lower() in p['name'].lower()]
    return render_template('index.html', products=filtered_products)

@app.route('/suggestions')
def suggestions():
    query = request.args.get('query', '')
    suggestions = [p['name'] for p in products if query.lower() in p['name'].lower()]
    return jsonify(suggestions=suggestions)

@app.route('/product/<name>')
def product(name):
    product = next((p for p in products if p['name'] == name), None)
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<name>', methods=['POST'])
def add_to_cart(name):
    quantity = int(request.form.get('quantity', 1))
    if 'cart' not in session:
        session['cart'] = []
    for _ in range(quantity):
        session['cart'].append(name)
    return jsonify(message=f"{name} added to cart")

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    cart_products = [p for p in products if p['name'] in cart_items]
    return render_template('cart.html', cart_products=cart_products)

@app.route('/remove_from_cart/<name>', methods=['POST'])
def remove_from_cart(name):
    quantity = int(request.form.get('quantity', 1))
    if 'cart' in session:
        for _ in range(quantity):
            if name in session['cart']:
                session['cart'].remove(name)
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        address = request.form['address']
        pincode = request.form['pincode']
        email = request.form['email']
        payment_method = request.form['payment_method']
        
        if not re.match(r'^\d{10}$', mobile):
            return render_template('checkout.html', error="Invalid mobile number")
        
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return render_template('checkout.html', error="Invalid email address")

        if 'orders' not in session:
            session['orders'] = []
        order = {
            'name': name,
            'mobile': mobile,
            'address': address,
            'pincode': pincode,
            'email': email,
            'payment_method': payment_method,
            'items': session.get('cart', [])
        }
        session['orders'].append(order)
        session['cart'] = []

        return render_template('order_confirmation.html', message="Thanks for your order! It will be delivered within 72 hours.")

    return render_template('checkout.html')

@app.route('/orders')
def orders():
    orders = session.get('orders', [])
    return render_template('orders.html', orders=orders)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if username in users:
            return render_template('signup.html', error="Username already exists")

        users[username] = {'password': password, 'email': email}
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('index'))
        
        return render_template('login.html', error="Invalid username or password")
    
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
