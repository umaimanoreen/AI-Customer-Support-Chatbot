from flask import Flask, request, jsonify, render_template_string
import spacy
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("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")

# Initialize NLP and Flask
nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)

def get_response(user_msg):
    doc = nlp(user_msg.lower())
    
    # Rule-based responses
    if any(token.text in ["order", "tracking"] for token in doc):
        return {"response": "Check your order status at: example.com/orders", "source": "rule"}
    elif any(token.text in ["return", "refund"] for token in doc):
        return {"response": "Returns accepted within 30 days", "source": "rule"}
    
    # AI response for other queries
    try:
        ai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}],
            temperature=0.7
        )
        return {"response": ai_response.choices[0].message.content, "source": "AI"}
    except Exception as e:
        return {"response": "I'm having technical difficulties", "source": "error"}

# Handle both GET and POST requests
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_msg = request.json.get('message')
    else:
        user_msg = request.args.get('message')
    return jsonify(get_response(user_msg))

# Root route with HTML form
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatbot Tester</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            form { margin: 20px 0; }
            input { padding: 8px; width: 300px; }
            button { padding: 8px 15px; }
            .response { margin-top: 20px; padding: 10px; background: #f5f5f5; }
        </style>
    </head>
    <body>
        <h1>Chatbot Tester</h1>
        <form onsubmit="sendMessage(event)">
            <input type="text" id="message" placeholder="Type your question...">
            <button type="submit">Send</button>
        </form>
        <div id="response" class="response"></div>
        
        <script>
            function sendMessage(e) {
                e.preventDefault();
                const message = document.getElementById('message').value;
                fetch('/chat?message=' + encodeURIComponent(message))
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('response').innerHTML = 
                            `<strong>Bot:</strong> ${data.response}`;
                    });
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)