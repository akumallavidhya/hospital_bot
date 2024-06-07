from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(debug=True)

