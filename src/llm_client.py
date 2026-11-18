import json
import urllib.request
import urllib.error

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"


def generate_response(prompt):

    # Prepare the request data
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "seed": 42
        }
    }

    # Convert Python dictionary into JSON
    json_data = json.dumps(data).encode("utf-8")

    # Create HTTP request
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        # Send request to Ollama
        with urllib.request.urlopen(request, timeout=120) as response:

            # Read response
            response_data = response.read().decode("utf-8")

            # Convert JSON response into Python dictionary
            result = json.loads(response_data)

            return result["response"]

    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not connect to Ollama: {error}")