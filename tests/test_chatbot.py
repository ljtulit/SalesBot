import requests
import json
import sys
from colorama import Fore, Style


# API endpoint
API_URL = 'http://localhost:8080/chatbot'
# Headers for the POST request
HEADERS = {'Content-Type': 'application/json'}

# Initialize conversation history
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


def send_request(text):
    global conversation_history
    # Add user's input to history
    conversation_history.append({"role": "user", "content": text})

    # Send POST request to chatbot endpoint with the entire conversation history
    response = requests.post(API_URL, headers=HEADERS,
                             data=json.dumps({'conversation': conversation_history}), stream=True)

    return response


def handle_response(response):
    print("Assistant: ")
    buffer = ""
    for chunk in response.iter_content(chunk_size=1):
        if chunk:
            char = chunk.decode('utf-8')
            if char != '\n':
                buffer += char
            else:
                json_response = json.loads(buffer)
                print_sentence(json_response['response'])
                # Add assistant's response to history
                conversation_history.append(
                    {"role": "assistant", "content": json_response['response']})
                buffer = ""


def print_sentence(sentence):
    print(f'{Fore.CYAN}{sentence}{Style.RESET_ALL}', end='', flush=True)


def test_chatbot():
    while True:
        text = get_user_input()
        response = send_request(text)
        handle_response(response)


if __name__ == '__main__':
    test_chatbot()
