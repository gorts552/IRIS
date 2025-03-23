from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text  
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy import or_
import logging
from fuzzywuzzy import process


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
# Function to return a greeting
def iris_greeting():
    return "Hello! I'm IRIS, your reproductive health assistant. How can I help you today?"
   

# Keyword Dictionary for Matching
KEYWORD_DICTIONARY ={
    "Greeting": [
        "hi", "hello", "hey", "good morning", "good evening", "whats up", 
        "yo", "sup", "how are you"
    ],
    "STIs": [
        "STI", "STD", "sexually transmitted infection", "sexually transmitted disease", 
        "sex infection", "disease from sex", "can I get an STI", "can I get an STD", 
        "what are STDs", "types of STIs", "common STDs"
    ],
    "STI Symptoms": [
        "STI symptoms", "STD symptoms", "signs of STI", "signs of STD", 
        "how do I know if I have an STI", "what does an STD feel like", "symptoms of gonorrhea", 
        "symptoms of chlamydia", "symptoms of herpes", "does an STI hurt"
    ],
    "STI Prevention": [
        "how to prevent STIs", "how to prevent STDs", "safe sex", "protection from STIs", 
        "can condoms prevent STDs", "how to avoid getting an STI", "safe sex tips"
    ],
    "HIV & AIDS": [
        "HIV", "AIDS", "can I get HIV", "what is HIV", "how does HIV spread", 
        "is HIV curable", "difference between HIV and AIDS", "how to prevent HIV", 
        "can you get HIV from kissing", "does HIV have symptoms", "HIV early symptoms"
    ],
    "Pregnancy Risk": [
        "pregnancy risk", "can I get pregnant", "pregnancy chance", "will I get pregnant", 
        "am I pregnant", "pregnancy symptoms", "what are the chances of pregnancy", 
         "can sperm on hands cause pregnancy"
    ],
    "Contraception": [
        "birth control", "contraception", "ways to prevent pregnancy", "condoms", 
        "IUD", "implant", "contraceptive patch", "contraceptive ring", "birth control pills", 
        "how to not get pregnant", "most effective birth control"
    ],
    "Emergency Contraception": [
        "morning after pill", "plan B", "emergency pill", "after sex pill", 
        "can I still prevent pregnancy", "how late can I take plan B", "how does the morning after pill work"
    ],
    "Menstruation": [
        "menstruation", "period", "that time of the month", "monthly bleeding", 
        "why do I get cramps", "period pain", "irregular periods", "why is my period late", 
        "how long does a period last", "period symptoms", "what does a normal period look like"
    ],
    "Adolescence & Puberty": [
        "adolescence", "puberty", "growing up", "body changes", "why is my voice deeper", 
        "why do I get acne", "why do I smell different", "body odor", "puberty signs", 
        "what happens during puberty", "why is my body changing", "why am I moody"
    ]
}


# Function to Match User Queries

def get_response(user_message):
    from iris_chatbot import db, HealthInfo, FAQTracking  # Moved inside, properly indented

    print(f"Received message: {user_message}")
    user_message = user_message.lower()
 # Check if the user is greeting IRIS
    if any(word in user_message for word in KEYWORD_DICTIONARY["Greeting"]):
        return iris_greeting()  # Call your greeting function

    # Try exact match first
    faq_entry = HealthInfo.query.filter(HealthInfo.question.ilike(f"%{user_message}%")).first()

    if not faq_entry:
        # Use fuzzy matching if no exact match is found
        all_questions = [q.question for q in HealthInfo.query.all()]
        best_match, score = process.extractOne(user_message, all_questions)

        if score >= 70:  # Only accept good matches (70% similarity or higher)
            faq_entry = HealthInfo.query.filter_by(question=best_match).first()
 
       
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
    
    return"I'm not sure I understand. Did you mean something about STIs, contraception,adolescence,menstruation or pregnancy?"


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


    