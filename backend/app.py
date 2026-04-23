from flask import Flask, jsonify, request
import mysql.connector
import os
import time

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'mysql-service'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'rootpassword123'),
    'database': os.environ.get('DB_NAME', 'three_tier_db')
}

def get_db():
    retries = 5
    for i in range(retries):
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except mysql.connector.Error:
            if i < retries - 1:
                time.sleep(3)
    return None

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'backend'})

@app.route('/api/data', methods=['GET'])
def get_data():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database unavailable'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name, created_at FROM items ORDER BY created_at DESC')
    items = cursor.fetchall()
    for item in items:
        item['created_at'] = str(item['created_at'])
    cursor.close()
    conn.close()
    return jsonify({'items': items})

@app.route('/api/data', methods=['POST'])
def add_data():
    data = request.get_json()
    name = data.get('name', '')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database unavailable'}), 500
    cursor = conn.cursor()
    cursor.execute('INSERT INTO items (name) VALUES (%s)', (name,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': f'Item "{name}" added successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
