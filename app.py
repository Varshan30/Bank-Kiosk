from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import errorcode

# (Optional future imports) random, string, datetime could be added when generating kiosk codes

app = Flask(__name__)
CORS(app)

# DB connection
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="varshan",
        database="bank_kiosk"
    )

db = get_db()
cursor = db.cursor(dictionary=True)

def ensure_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            email VARCHAR(160) NOT NULL UNIQUE,
            phone VARCHAR(20) NOT NULL,
            passcode VARCHAR(10) NOT NULL,
            balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    db.commit()

ensure_tables()

# Health check
@app.route('/')
def home():
    return jsonify(message='Bank Kiosk API running')

# User signup
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email').lower()
    phone = data.get('phone')
    passcode = data.get('passcode')

    if not (name and email and phone and passcode):
        return jsonify(error='missing_fields'), 400

    try:
        cursor.execute("SELECT id FROM auth_users WHERE email=%s", (email,))
    except mysql.connector.Error as e:
        # Attempt to recover if table missing
        ensure_tables()
        cursor.execute("SELECT id FROM auth_users WHERE email=%s", (email,))
    if cursor.fetchone():
        return jsonify(error='exists'), 409

    cursor.execute("INSERT INTO auth_users (name,email,phone,passcode) VALUES (%s,%s,%s,%s)",
                   (name, email, phone, passcode))
    db.commit()
    return jsonify(ok=True, user={'id': cursor.lastrowid, 'name': name, 'email': email, 'phone': phone, 'balance': 0})

# Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email').lower()
    passcode = data.get('passcode')

    cursor.execute("SELECT * FROM auth_users WHERE email=%s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify(error='no_user'), 404
    if user['passcode'] != passcode:
        return jsonify(error='bad_creds'), 401

    return jsonify(user={'id': user['id'], 'name': user['name'], 'email': user['email'], 'phone': user['phone'], 'balance': float(user['balance'])})

# Deposit
@app.route('/deposit', methods=['POST'])
def deposit():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = float(data.get('amount'))

    cursor.execute("UPDATE auth_users SET balance = balance + %s WHERE id=%s", (amount, user_id))
    db.commit()
    return jsonify(message='Deposit successful')

# Withdraw
@app.route('/withdraw', methods=['POST'])
def withdraw():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = float(data.get('amount'))

    cursor.execute("SELECT balance FROM auth_users WHERE id=%s", (user_id,))
    bal = cursor.fetchone()
    if bal and bal['balance'] >= amount:
        cursor.execute("UPDATE auth_users SET balance = balance - %s WHERE id=%s", (amount, user_id))
        db.commit()
        return jsonify(message='Withdrawal successful')
    else:
        return jsonify(error='insufficient_funds'), 400

# Balance check
@app.route('/balance', methods=['GET'])
def balance():
    user_id = request.args.get('user_id')
    cursor.execute("SELECT balance FROM auth_users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    return jsonify(balance=float(user['balance']) if user else 0)

if __name__ == '__main__':
    app.run(debug=True)
