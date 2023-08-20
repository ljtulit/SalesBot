import os
import openai

API_KEY = os.getenv('OPENAI_API_KEY')


def get_system_message(filename):
    with open(filename, 'r') as file:
        return file.read().strip()


def compose_conversation(history, new_message, system_filename):
    # Only add system message if the history is empty
    if not history:
        system_message = get_system_message(system_filename)
        history.append({"role": "system", "content": system_message})

    # Do not add user's message as it's already appended on the client-side
    # If the 'assistant' role is added here, it should be after the response is generated.

    return history


def generate_chat_response(conversation):
    print(conversation)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=conversation,
        stream=True,
    )
    for message in response:
        if 'content' in message.choices[0].delta:
            yield message.choices[0].delta.content
        elif 'finish_reason' in message.choices[0] and message.choices[0]['finish_reason'] == 'stop':
            break  # Stop iterating when the model has finished generating tokens
        else:
            print(f"Unexpected response: {message}")
