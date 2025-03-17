from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
from pyngrok import ngrok  
from pyngrok import ngrok
tunnel = ngrok.connect(5000)
print(f"ngrok URL: {tunnel.public_url}")


# Initialize Flask App 
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:celinemysql#1@localhost/iris_chatbot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Models
class HealthInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)

class FAQTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('health_info.id'), nullable=False)
    access_count = db.Column(db.Integer, default=0)

    question = db.relationship('HealthInfo', backref=db.backref('faq_tracking', lazy=True))

# Function to Match User Queries
def get_response(user_message):
    user_message = user_message.lower()
    faq_entry = HealthInfo.query.filter(HealthInfo.question.like(f"%{user_message}%")).first()  

    if faq_entry:
        # Update FAQ tracking count
        faq_track = FAQTracking.query.filter_by(question_id=faq_entry.id).first()
        if faq_track:
            faq_track.access_count += 1
        else:
            faq_track = FAQTracking(question_id=faq_entry.id, access_count=1)
            db.session.add(faq_track)

        db.session.commit()
        return faq_entry.answer
    else:
        return "I'm sorry, please rephrase your question."

# Flask Routes
@app.route('/')
def home():
    return render_template("chat.html")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').lower()  

    # Search for a matching question in the database
    faq_entry = HealthInfo.query.filter_by(question=user_message).first()

    if faq_entry:
        bot_response = faq_entry.answer  
    else:
        bot_response = "I'm sorry, I don't have an answer for that yet. Please try rephrasing."

    return jsonify({"response": bot_response})

@app.route('/webhook', methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip()
    response_text = get_response(incoming_msg)

    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

# Ensure Database Tables Exist
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

# Run Flask App (Only One `if __name__ == "__main__"` Block)
if __name__ == "__main__":
    app.run(debug=True)
