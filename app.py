from flask import Flask, render_template, request
from textblob import TextBlob
import sqlite3
from model import predict_category
import uuid
import smtplib
import nltk
nltk.download('punkt')

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_id TEXT,
        text TEXT,
        category TEXT,
        urgency TEXT,
        sentiment TEXT
    )
    """)
    conn.commit()
    conn.close()
init_db()

# ---------- LOGIC ----------
def detect_urgency(text):
    if "urgent" in text or "immediately" in text:
        return "High"
    elif "soon" in text:
        return "Medium"
    else:
        return "Low"

# ---------- EMAIL ----------
def send_email_alert(complaint):
    sender = "ashrithlucky8@gmail.com"
    password = "aoolvremcdtpztoy"
    message = f"URGENT COMPLAINT:\n\n{complaint}"
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, sender, message)
    server.quit()

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":

        complaint = request.form["complaint"]
        tracking_id = str(uuid.uuid4())[:8]

        category = predict_category(complaint)
        urgency = detect_urgency(complaint)

        sentiment_score = TextBlob(complaint).sentiment.polarity

        if sentiment_score < 0:
            mood = "Negative 😡"
        elif sentiment_score == 0:
            mood = "Neutral 😐"
        else:
            mood = "Positive 🙂"

        # 📧 SEND EMAIL IF HIGH
       # if urgency == "High":
        #    send_email_alert(complaint)

        # 💾 SAVE TO DATABASE
        conn = sqlite3.connect("/tmp/complaints.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO complaints (tracking_id, text, category, urgency, sentiment) VALUES (?, ?, ?, ?, ?)",
            (tracking_id, complaint, category, urgency, mood)
        )

        conn.commit()
        conn.close()

        # 🎯 RESULT TO FRONTEND
        result = {
            "category": category,
            "urgency": urgency,
            "sentiment": mood,
            "tracking_id": tracking_id
        }

    return render_template("index.html", result=result)

# ---------- HISTORY ----------
@app.route("/history")
def history():
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints")
    data = cursor.fetchall()

    conn.close()

    return render_template("history.html", data=data)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)