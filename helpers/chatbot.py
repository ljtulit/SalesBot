import os
import openai

API_KEY = os.getenv('OPENAI_API_KEY')

# Make sure to initialize the OpenAI key
openai.api_key = API_KEY

def compose_conversation(history, new_message, system_message=None):
    # Prepend system message to history if provided
    if system_message:
        history.insert(0, {"role": "system", "content": system_message})
    # Append user's message to history
    if new_message:
        history.append({"role": "user", "content": new_message})
    return history

def generate_chat_response(conversation):
    # Read the system message from system.txt
    with open('helpers/system.txt', 'r') as file:
        system_message = file.read().strip()  # Read and strip any excess whitespace

    # Prepend the conversation with the system message
    updated_conversation = compose_conversation(conversation, '', system_message)

    # Use OpenAI API to generate a response based on the full conversation
    print(f"Sending conversation to OpenAI: {updated_conversation}")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=updated_conversation,
        stream=True,
    )
    
    for message in response:
        if 'content' in message.choices[0].delta:
            yield message.choices[0].delta.content
        elif 'finish_reason' in message.choices[0] and message.choices[0]['finish_reason'] == 'stop':
            break  # Stop iterating when the model has finished generating tokens
        else:
            print(f"Unexpected response: {message}")
