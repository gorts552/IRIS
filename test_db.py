from flask import Flask, app,render_template,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy import create_engine

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

try:
    with engine.connect() as connection:
        print("✅ Connected to PostgreSQL successfully!")
except Exception as e:
    print("❌ Connection failed:", e)

 #Database Configuration (PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://iris_chatbot_user:rWy6A23qAb988nQxwMSTl8gPsjzRSUO3@dpg-cvd8igl2ng1s73drfbd0-a:5432/iris_chatbot'

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

