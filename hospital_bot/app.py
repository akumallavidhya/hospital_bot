from flask import Flask, request, jsonify, render_template
import sqlite3
import requests
import os
import hmac
import hashlib
import time
import base64
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv('AIzaSyAwGpq7DtCDPvcuMdXI80xCXw3sPZu0a90')
GEMINI_API_SECRET = os.getenv('GEMINI_API_SECRET').encode()

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            contact TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor TEXT,
            date TEXT,
            time TEXT,
            reason TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_patient', methods=['POST'])
def add_patient():
    data = request.get_json()
    name = data['name']
    age = data['age']
    gender = data['gender']
    contact = data['contact']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO patients (name, age, gender, contact) VALUES (?, ?, ?, ?)', (name, age, gender, contact))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Patient added successfully!'})

@app.route('/schedule_appointment', methods=['POST'])
def schedule_appointment():
    data = request.get_json()
    patient_id = data['patient_id']
    doctor = data['doctor']
    date = data['date']
    time = data['time']
    reason = data['reason']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO appointments (patient_id, doctor, date, time, reason) VALUES (?, ?, ?, ?, ?)',
              (patient_id, doctor, date, time, reason))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Appointment scheduled successfully!'})

@app.route('/get_patients')
def get_patients():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM patients')
    patients = c.fetchall()
    conn.close()
    return jsonify(patients)

@app.route('/get_appointments')
def get_appointments():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM appointments')
    appointments = c.fetchall()
    conn.close()
    return jsonify(appointments)

@app.route('/show_patients')
def show_patients():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM patients')
    patients = c.fetchall()
    conn.close()
    return render_template('patients.html', patients=patients)

@app.route('/show_appointments')
def show_appointments():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        SELECT appointments.id, patients.name, appointments.doctor, appointments.date, appointments.time, appointments.reason 
        FROM appointments
        JOIN patients ON appointments.patient_id = patients.id
    ''')
    appointments = c.fetchall()
    conn.close()
    return render_template('appointments.html', appointments=appointments)

# Function to fetch Gemini API data
def fetch_gemini_data(symbol):
    url = f'https://api.gemini.com/v1/pubticker/{symbol}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch data from Gemini'}

@app.route('/get_crypto_price/<symbol>')
def get_crypto_price(symbol):
    data = fetch_gemini_data(symbol)
    return jsonify(data)

# Function to fetch Gemini API data with authentication
def fetch_authenticated_gemini_data(endpoint):
    base_url = 'https://api.gemini.com'
    url = base_url + endpoint
    nonce = str(int(time.time() * 1000))
    payload = {
        'request': endpoint,
        'nonce': nonce
    }
    payload_encoded = base64.b64encode(json.dumps(payload).encode())
    signature = hmac.new(GEMINI_API_SECRET, payload_encoded, hashlib.sha384).hexdigest()

    headers = {
        'X-GEMINI-APIKEY': GEMINI_API_KEY,
        'X-GEMINI-PAYLOAD': payload_encoded,
        'X-GEMINI-SIGNATURE': signature,
        'Content-Type': 'text/plain'
    }

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch authenticated data from Gemini'}

@app.route('/get_authenticated_data')
def get_authenticated_data():
    endpoint = '/v1/account'
    data = fetch_authenticated_gemini_data(endpoint)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)


