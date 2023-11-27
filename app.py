from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import json
from helpers.chatbot import generate_chat_response
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/chatbot": {"origins": "*"}})

@app.route('/chatbot', methods=['POST'])
def chat():
    print("test")
    data = request.json
    conversation = data.get('messages', [])  # Expecting 'messages' from the client
    
    #logging.info(f"Conversation so far: {conversation}")

    def generate():
        for response in generate_chat_response(conversation):
            logging.info(f"Generated response: {response}")
            # Yield each response chunk
            yield json.dumps({'response': response}).encode('utf-8') + b'\n'
        logging.info("Finished generating responses.")

    return Response(stream_with_context(generate()), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
