from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import json
from helpers.chatbot import generate_chat_response
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
CORS(app)

@app.route('/chatbot', methods=['POST'])
def chat():
    data = request.json
    input_text = data.get('text')
    conversation = data.get('history', [])  # Get the full history if provided
    
    logging.info(f"Received input: {input_text}")
    logging.info(f"Conversation so far: {conversation}")

    def generate():
        # Generate a response
        for response in generate_chat_response(conversation):
            logging.info(f"Generated response: {response}")
            # Yield each chunk as it's ready
            yield json.dumps({'response': response}).encode('utf-8') + b'\n'
        logging.info("Finished generating responses.")

    return Response(stream_with_context(generate()), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
