# GoodbyeQuota

GoodbyeQuota is a Python library designed to wrap the Google Gemini API (`google-generativeai`) and automatically manage multiple API keys. If one key hits a quota limit (`ResourceExhausted`), the library automatically switches to another key and retries the request.

## Installation

```bash
pip install .
```

## Usage

### Basic Generation

```python
from goodbye_quota import GoodbyeQuota

# List of your API keys
api_keys = [
    "AIzaSy...",
    "AIzaSy...",
    "AIzaSy..."
]

# Initialize the client
client = GoodbyeQuota(api_keys)

# Create a model (same API as genai.GenerativeModel)
model = client.create_model("gemini-pro")

# Generate content
try:
    response = model.generate_content("Tell me a joke about quotas.")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
```

### Chat Session

```python
chat = model.start_chat()
response = chat.send_message("Hello!")
print(response.text)
```

## How it works

The library maintains a list of API keys. When you make a request, it configures the `google.generativeai` global state with one of the keys. If a `ResourceExhausted` error occurs, it marks that key as exhausted (with a cooldown), picks a new key, and retries the request automatically.
