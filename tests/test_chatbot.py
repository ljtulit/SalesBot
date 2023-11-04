import requests
import json
from halo import Halo
import sys
from colorama import Fore, Style
import logging

# API endpoint
API_URL = 'http://localhost:8080/chatbot'
# Headers for the POST request
HEADERS = {'Content-Type': 'application/json'}

conversation_history = []


def get_user_input():
    while True:
        text = input('\n\nUSER: ')
        # check if user wants to exit
        if 'DONE' in text:
            print('\n\n\nExiting Program...')
            sys.exit(0)
        # if empty submission, probably on accident, continue
        if text == '':
            continue
        return text
    
def compose_conversation(history, new_message, assistant_role=None):
    # Append user's message
    history.append({"role": "user", "content": new_message})
    
    # If there's an assistant's role message, append it (first time setup or special cases)
    if assistant_role:
        history.append({"role": "assistant", "content": assistant_role})
    
    return history

def send_request(text, history):
    # Now send the full history with each request
    response = requests.post(API_URL, headers=HEADERS,
                             data=json.dumps({'text': text, 'history': history}), stream=True)
    return response


# In the `handle_response` function, make sure you update the conversation history with the bot's response
def handle_response(response):
    print("Assistant: ")
    buffer = ""
    for chunk in response.iter_content(chunk_size=1):
        if chunk:
            char = chunk.decode('utf-8')
            if char != '\n':
                buffer += char
            else:
                logging.debug(f"Received chunk: {buffer}")
                json_response = json.loads(buffer)
                response_text = json_response['response']
                # Add the bot's response to the conversation history
                conversation_history.append({"role": "assistant", "content": response_text})
                print_sentence(response_text)
                buffer = ""
        else:
            logging.debug("Received empty chunk.")
    logging.debug("End of response stream.")


def print_sentence(sentence):
    print(f'{Fore.CYAN}{sentence}{Style.RESET_ALL}', end='', flush=True)


def test_chatbot():
    global conversation_history  # Reference the global conversation history
    while True:
        text = get_user_input()
        compose_conversation(conversation_history, text)  # Pass only the user text, no assistant_role here
        response = send_request(text, conversation_history)
        handle_response(response)

if __name__ == '__main__':
    test_chatbot()
