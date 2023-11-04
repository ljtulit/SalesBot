


async function* streamGenerator(response) {
    const reader = response.body.getReader();
    let { value: chunk, done: readerDone } = await reader.read();
    chunk = chunk ? new TextDecoder("utf-8").decode(chunk) : "";

    console.log('Initial chunk:', chunk); // Debug print

    let reassembledString = "";

    while (!readerDone) {
        const re = /\n|\r|\r\n/; // Regular expression to match new line characters
        let result = chunk.match(re);

        while (result) {
            console.log('Result found:', result[0]); // Debug print
            reassembledString += chunk.substring(0, result.index);
            console.log('Reassembled string before JSON parse:', reassembledString); // Debug print

            chunk = chunk.substring(result.index + result[0].length);

            if (reassembledString.trim()) {
                try {
                    const json = JSON.parse(reassembledString);
                    console.log('Parsed JSON:', json); // Debug print
                    if (json.response && json.response.trim() !== "") {
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
        console.log('Reassembled string outside loop:', reassembledString); // Debug print

        // Read the next chunk
        ({ value: chunk, done: readerDone } = await reader.read());
        chunk = chunk ? new TextDecoder("utf-8").decode(chunk) : "";
        console.log('New chunk:', chunk); // Debug print
    }

    // Once the stream is finished, try to parse any remaining text
    if (reassembledString.trim()) {
        try {
            const json = JSON.parse(reassembledString);
            console.log('Final parsed JSON:', json); // Debug print
            if (json.response && json.response.trim() !== "") {
                yield json.response;
            }
        } catch (e) {
            console.error("Final error parsing JSON:", e, "with string:", reassembledString);
        }
    }
}



function sendMessage() {
    var message = document.getElementById("message").value;
    if (message.trim() === '') {
        return false;
    }
    appendMessage("user", message);
    document.getElementById("message").value = '';

    fetch("http://localhost:8080/chatbot", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ "text": message, "history": conversationHistory }),
    })
        .then(async (response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            } else {
                // Since we want to append text to the same message element, we need to get that element
                let lastMessageElement;
                for await (const chunk of streamGenerator(response)) {
                    if (!lastMessageElement) {
                        lastMessageElement = appendMessage("bot", chunk, true); // Pass true to indicate that this is a streaming message
                    } else {
                        lastMessageElement.textContent += chunk;
                    }
                    // Make sure we scroll to the bottom each time new text is added
                    var chatContainer = document.getElementById("chat-container");
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }
        })
        .catch((error) => {
            console.error('Fetch error:', error);
        });
}

var conversationHistory = [];

function appendMessage(sender, message, isStream = false) {
    var chatContainer = document.getElementById("chat-container");
    var messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);

    // If it's part of a stream, we still create the element but may not set text yet.
    if (!isStream || message) {
        messageDiv.textContent = message;
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    return messageDiv; // Return the element so we can keep appending text to it
}