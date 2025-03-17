from flask import Flask, app,render_template,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:celinemysql#1@localhost/iris_chatbot")

try:
    with engine.connect() as connection:
        print("✅ Connected to MySQL successfully!")
except Exception as e:
    print("❌ Connection failed:", e)

 #Database Configuration (MYSql)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:celinemysql#1@localhost/iris_chatbot'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Health Information (Stores Q&A for IRIS)
class HealthInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    #Create Database Tables
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("Database tables created successfully!")

