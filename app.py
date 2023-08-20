from flask import Flask, request, Response, stream_with_context, session
import json
from helpers.chatbot import compose_conversation, generate_chat_response
from datetime import timedelta

app = Flask(__name__)
# Set a secret key for session management
app.secret_key = 'your_secret_key'
# Set the session lifetime if you wish
app.permanent_session_lifetime = timedelta(minutes=30)


@app.route('/chatbot', methods=['POST'])
def chat():
    # Get the conversation history from the request body
    conversation = request.json.get('conversation', [])

    # Get the latest user input from the conversation history
    input_text = conversation[-1]['content'] if conversation else ''

    # Add the user's input and the assistant's role to the conversation
    conversation = compose_conversation(
        conversation, input_text, "system_message.txt")

    def generate():
        # Generate a response
        for response in generate_chat_response(conversation):
            # Save updated conversation to session
            session['conversation'] = conversation
            # Yield each chunk as it's ready
            yield json.dumps({'response': response}).encode('utf-8') + b'\n'

    return Response(stream_with_context(generate()), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
