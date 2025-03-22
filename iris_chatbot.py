from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text  
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy import or_
from iris_chatbot import db, HealthInfo, FAQTracking  # Adjust import based on your setup
import logging

# Initialize Flask App 
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://iris_chatbot_user:rWy6A23qAb988nQxwMSTl8gPsjzRSUO3@dpg-cvd8igl2ng1s73drfbd0-a.oregon-postgres.render.com/iris_chatbot?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Test Database Connection at Startup
with app.app_context():  
    try:
        print("Checking database connection...")
        result = db.session.execute(text("SELECT 1")).fetchall()
        print(f"✅ Database connection successful! Result: {result}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

# Define Models
class HealthInfo(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)

class FAQTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('health_info.question_id'), nullable=False)
    access_count = db.Column(db.Integer, default=0)

    question = db.relationship('HealthInfo', backref=db.backref('faq_tracking', lazy=True))

# Keyword Dictionary for Matching
KEYWORD_DICTIONARY = {
    "pregnancy": ["pregnant", "conception", "fertility"],
    "menstruation": ["period", "menstrual cycle", "cramps"],
    "contraception": ["birth control", "condom", "pill","morning after pill"],
    "STI": ["STD", "infection", "HIV", "herpes","gonorrhea","chlamydia"]
     
}

# Function to Match User Queries
def get_response(user_message):
    print(f"Received message: {user_message}")
    user_message = user_message.lower()
    
    # Try exact match first
    faq_entry = HealthInfo.query.filter(HealthInfo.question.ilike(f"%{user_message}%")).first()
    
    if not faq_entry:
        # Token-based keyword matching
        words = user_message.split()
        matched_questions = set()

        for word in words:
            for key, synonyms in KEYWORD_DICTIONARY.items():
                if word in synonyms or word == key:
                    matched_questions.add(key)

        if matched_questions:
            faq_entry = HealthInfo.query.filter(
                or_(*[HealthInfo.question.ilike(f"%{keyword}%") for keyword in matched_questions])
            ).first()
    
    if faq_entry:
        # Update FAQ tracking count
        faq_track = FAQTracking.query.filter_by(question_id=faq_entry.question_id).first()
        if faq_track:
            faq_track.access_count += 1
        else:
            faq_track = FAQTracking(question_id=faq_entry.question_id, access_count=1)
            db.session.add(faq_track)
        
        db.session.commit()
        return faq_entry.answer
    
    return "I'm sorry, please rephrase your question."

# Flask Routes
@app.route('/')
def home():
    return render_template("chat.html")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').lower()
    bot_response = get_response(user_message)
    return jsonify({"response": bot_response})

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("flask_logs.txt"),
        logging.StreamHandler()
    ]
)

@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_reply():
    if request.method == 'GET':
        return "✅ Webhook is live!", 200
    
    incoming_msg = request.values.get('Body', '').strip()
    logging.info(f"Received WhatsApp message: {incoming_msg}")
    
    response_text = get_response(incoming_msg)
    logging.info(f"Bot response: {response_text}")
    
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

# Ensure Database Tables Exist
with app.app_context():
    db.create_all()

print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
print("✅ Database tables created successfully!")

# Run Flask App
if __name__ == "__main__":
    app.run(port=5432, debug=True)


    