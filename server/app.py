"""
ESPMonitor Flask Server
Main application entry point
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'espmonitor.db')

# Global thresholds (stored in DB, cached here)
thresholds = {
    'temperature': 30.0,
    'humidity': 70.0,
    'water_level': 80.0
}


# ==================== Database Functions ====================
def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Sensor data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            water_level REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Thresholds table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thresholds (
            id INTEGER PRIMARY KEY,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            water_level REAL NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default thresholds if not exists
    cursor.execute('SELECT COUNT(*) FROM thresholds')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO thresholds (id, temperature, humidity, water_level)
            VALUES (1, 30.0, 70.0, 80.0)
        ''')

    conn.commit()
    conn.close()
    print("Database initialized")


def load_thresholds():
    """Load thresholds from database into memory"""
    global thresholds
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT temperature, humidity, water_level FROM thresholds WHERE id = 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        thresholds['temperature'] = row[0]
        thresholds['humidity'] = row[1]
        thresholds['water_level'] = row[2]


def save_sensor_data(device_id, temperature, humidity, water_level):
    """Save sensor reading to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (device_id, temperature, humidity, water_level)
        VALUES (?, ?, ?, ?)
    ''', (device_id, temperature, humidity, water_level))
    conn.commit()
    conn.close()


def get_latest_data(limit=20):
    """Get latest sensor readings"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT device_id, temperature, humidity, water_level, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            'device_id': row[0],
            'temperature': row[1],
            'humidity': row[2],
            'water_level': row[3],
            'timestamp': row[4]
        })
    return data


def update_thresholds(temp, humidity, water):
    """Update thresholds in database and cache"""
    global thresholds
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE thresholds
        SET temperature = ?, humidity = ?, water_level = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
    ''', (temp, humidity, water))
    conn.commit()
    conn.close()

    # Update cache
    thresholds['temperature'] = temp
    thresholds['humidity'] = humidity
    thresholds['water_level'] = water


# ==================== API Routes ====================

@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('dashboard.html')


@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    """Receive sensor data from ESP32"""
    try:
        data = request.get_json()

        # Validate required fields
        required = ['temperature', 'humidity', 'water_level', 'device_id']
        if not all(key in data for key in required):
            return jsonify({'error': 'Missing required fields'}), 400

        # Save to database
        save_sensor_data(
            data['device_id'],
            data['temperature'],
            data['humidity'],
            data['water_level']
        )

        print(f"Data received from {data['device_id']}: "
              f"T={data['temperature']}°C, H={data['humidity']}%, W={data['water_level']}%")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/latest-data', methods=['GET'])
def get_latest():
    """Get latest sensor readings"""
    try:
        limit = request.args.get('limit', 20, type=int)
        data = get_latest_data(limit)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/thresholds', methods=['GET'])
def get_thresholds():
    """Get current thresholds"""
    return jsonify(thresholds), 200


@app.route('/api/thresholds', methods=['POST'])
def set_thresholds():
    """Update thresholds"""
    try:
        data = request.get_json()

        temp = float(data.get('temperature', thresholds['temperature']))
        humidity = float(data.get('humidity', thresholds['humidity']))
        water = float(data.get('water_level', thresholds['water_level']))

        update_thresholds(temp, humidity, water)

        print(f"Thresholds updated: T={temp}°C, H={humidity}%, W={water}%")

        return jsonify({'status': 'success', 'thresholds': thresholds}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get historical data with filtering"""
    try:
        device_id = request.args.get('device_id')
        limit = request.args.get('limit', 100, type=int)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if device_id:
            cursor.execute('''
                SELECT device_id, temperature, humidity, water_level, timestamp
                FROM sensor_data
                WHERE device_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (device_id, limit))
        else:
            cursor.execute('''
                SELECT device_id, temperature, humidity, water_level, timestamp
                FROM sensor_data
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        data = []
        for row in rows:
            data.append({
                'device_id': row[0],
                'temperature': row[1],
                'humidity': row[2],
                'water_level': row[3],
                'timestamp': row[4]
            })

        return jsonify(data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistical summary"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get stats for last 24 hours
        cursor.execute('''
            SELECT
                AVG(temperature) as avg_temp,
                MAX(temperature) as max_temp,
                MIN(temperature) as min_temp,
                AVG(humidity) as avg_hum,
                MAX(humidity) as max_hum,
                MIN(humidity) as min_hum,
                AVG(water_level) as avg_water,
                MAX(water_level) as max_water,
                MIN(water_level) as min_water,
                COUNT(*) as total_readings
            FROM sensor_data
            WHERE timestamp >= datetime('now', '-24 hours')
        ''')

        row = cursor.fetchone()
        conn.close()

        if row and row[9] > 0:  # total_readings > 0
            stats = {
                'temperature': {
                    'avg': round(row[0], 2),
                    'max': round(row[1], 2),
                    'min': round(row[2], 2)
                },
                'humidity': {
                    'avg': round(row[3], 2),
                    'max': round(row[4], 2),
                    'min': round(row[5], 2)
                },
                'water_level': {
                    'avg': round(row[6], 2),
                    'max': round(row[7], 2),
                    'min': round(row[8], 2)
                },
                'total_readings': row[9]
            }
        else:
            stats = {'message': 'No data available'}

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Main ====================
if __name__ == '__main__':
    print("=== ESPMonitor Server Starting ===")

    # Ensure database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Initialize database
    init_db()

    # Load thresholds
    load_thresholds()
    print(f"Current thresholds: {thresholds}")

    # Start server
    app.run(host='0.0.0.0', port=8080, debug=True)
