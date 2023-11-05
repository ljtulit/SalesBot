// Initialize the conversation history
var conversationHistory = [];

// Function to add a message to the chat window and the conversation history
function appendMessage(sender, message, isStream = false) {
    var chatContainer = document.getElementById("chat-container");
    var messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);

    if (!isStream || message) {
        messageDiv.textContent = message;
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Only update the conversation history if it's not a stream
    if (!isStream) {
        conversationHistory.push({ role: sender, content: message });
    }

    return messageDiv;
}

// Function to handle the stream of messages from the server
async function* streamGenerator(response) {
    const reader = response.body.getReader();
    let { value: chunk, done: readerDone } = await reader.read();
    chunk = chunk ? new TextDecoder("utf-8").decode(chunk) : "";

    let reassembledString = "";

    while (!readerDone) {
        const re = /\n|\r|\r\n/; // Match new line characters
        let result = chunk.match(re);

        while (result) {
            reassembledString += chunk.substring(0, result.index);
            chunk = chunk.substring(result.index + result[0].length);

            if (reassembledString) {
                try {
                    const json = JSON.parse(reassembledString);
                    if (json.response !== "") {
                        yield json.response;
                    }
                } catch (e) {
                    console.error("Error parsing JSON:", e, "with string:", reassembledString);
                }
            }
            reassembledString = "";
            result = chunk.match(re);
        }

        reassembledString += chunk;

        ({ value: chunk, done: readerDone } = await reader.read());
        chunk = chunk ? new TextDecoder("utf-8").decode(chunk) : "";
    }

    // Parse any remaining text after the stream is finished
    if (reassembledString.trim()) {
        try {
            const json = JSON.parse(reassembledString);
            if (json.response && json.response.trim() !== "") {
                yield json.response;
            }
        } catch (e) {
            console.error("Final error parsing JSON:", e, "with string:", reassembledString);
        }
    }
}

// Function to send a message to the server
function sendMessage() {
    var messageInput = document.getElementById("message");
    var message = messageInput.value.trim();

    if (message === '') {
        return;
    }

    appendMessage("user", message);
    messageInput.value = '';

    fetch("http://localhost:8080/chatbot", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ "messages": conversationHistory }),
    })
        .then(async (response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            let lastMessageElement;
            for await (const chunk of streamGenerator(response)) {
                if (!lastMessageElement) {
                    lastMessageElement = appendMessage("bot", chunk, true); // Indicate streaming message
                } else {
                    lastMessageElement.textContent += chunk;
                }
                var chatContainer = document.getElementById("chat-container");
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        })
        .catch((error) => {
            console.error('Fetch error:', error);
        });
}

// Event listener for DOMContentLoaded to set up the chat interface
document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('open-chat').addEventListener('click', openChat);

    openChat()
});

function openChat() {
    var assistantContainer = document.getElementById('assistant-container');
    var openChat = document.getElementById('open-chat');

    assistantContainer.classList.add('active');
    openChat.classList.remove('active');
}

function closeChat() {
    var assistantContainer = document.getElementById('assistant-container');
    var openChat = document.getElementById('open-chat');

    assistantContainer.classList.remove('active');
    openChat.classList.add('active');
}