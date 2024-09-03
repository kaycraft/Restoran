from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'secret_key'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            people INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        date = request.form['date']
        time = request.form['time']
        people = request.form['people']

        conn = get_db_connection()
        conn.execute('INSERT INTO reservations (name, email, phone, date, time, people, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (name, email, phone, date, time, people, 'Booked'))
        conn.commit()
        conn.close()

        send_confirmation_email(name, email, date, time)

        flash('Reservation successful! A confirmation email has been sent.')
        return redirect(url_for('index'))

    return render_template('reserve.html')

@app.route('/admin')
def admin():
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()
    return render_template('admin.html', reservations=reservations)

@app.route('/cancel/<int:id>', methods=['POST'])
def cancel(id):
    conn = get_db_connection()
    conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('Cancelled', id))
    conn.commit()
    conn.close()

    flash('Reservation cancelled.')
    return redirect(url_for('admin'))

def send_confirmation_email(name, email, date, time):
    sender_email = "youremail@example.com"
    sender_password = "yourpassword"
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Reservation Confirmation"
    message["From"] = sender_email
    message["To"] = email

    text = f"Hi {name},\n\nYour reservation for {date} at {time} has been confirmed.\n\nThank you for choosing our restaurant!"
    part = MIMEText(text, "plain")
    message.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())

if __name__ == '__main__':
    init_db()  # Initialize database
    app.run(debug=True)