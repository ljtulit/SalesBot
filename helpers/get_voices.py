import requests

url = "https://api.elevenlabs.io/v1/voices"

headers = {
    "Accept": "application/json",
    "xi-api-key": "0d0928925dd61d3caab422396fa75355"
}

response = requests.get(url, headers=headers)

print(response.text)
