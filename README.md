[![f5So56g.md.png](https://iili.io/f5So56g.md.png)](https://freeimage.host/i/f5So56g)

**Never let a 429 error stop your AI agents again.**

`GoodbyeQuota` is a robust Python wrapper for the Google Gemini API (`google-generativeai`) that manages a pool of API keys. When one key hits its rate limit or quota (`ResourceExhausted`), this library **automatically** switches to the next available key and retries the request seamlessly.

Your code doesn't crash. Your users don't wait. It just works.

---

## ✨ Features

- **🔄 Smart Key Rotation**: Automatically cycles through a list of API keys when quotas are hit.
- **⏱️ Intelligent Cooldowns**: Temporarily sidelines exhausted keys so they can recover.
- **💬 Chat Persistence**: Seamlessly handles key switching even inside active chat sessions.
- **🔌 Drop-in Replacement**: Designed to look and feel exactly like the standard `google-generativeai` library.
- **🛡️ Fault Tolerance**: Handles transient service errors (500/503) with automatic retries.

## 📦 Installation

Clone the repository and install locally:

```bash
git clone https://github.com/yourusername/GoodbyeQuota.git
cd GoodbyeQuota
pip install .
```

## 🚀 Usage

### 1. Basic Generation

Just pass a list of keys instead of a single one.

```python
from goodbye_quota import GoodbyeQuota

# 1. Define your pool of keys
api_keys = [
    "AIzaSy...Key1",
    "AIzaSy...Key2",
    "AIzaSy...Key3",
    # Add as many as you want!
]

# 2. Initialize the client
client = GoodbyeQuota(api_keys)

# 3. Create a model (Just like standard Gemini)
model = client.create_model("gemini-pro")

# 4. Generate content without fear
try:
    response = model.generate_content("Explain quantum computing in 5 words.")
    print(f"🤖 AI: {response.text}")
except Exception as e:
    print(f"❌ Failed: {e}")
```

### 2. Chat Sessions

`GoodbyeQuota` maintains the chat history even if the underlying API key changes mid-conversation.

```python
# Start a chat
chat = model.start_chat(history=[])

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break
    
    # If Key #1 dies here, Key #2 takes over instantly
    response = chat.send_message(user_input)
    print(f"Gemini: {response.text}")
```

### 3. Configuration Strategies

You can choose how keys are selected:

- **`round_robin`** (Default): Cycles through keys in order (1 -> 2 -> 3 -> 1). Best for fair usage.
- **`random`**: Picks a random valid key for each request.

```python
client = GoodbyeQuota(api_keys, strategy="random")
```

## 🧠 How It Works

1. **Initialization**: You provide a list of valid Gemini API keys.
2. **Execution**: When you call `.generate_content()` or `.send_message()`, the library configures the global Gemini environment with the current active key.
3. **Error Handling**:
   - If a `429 ResourceExhausted` error occurs:
     - The current key is marked as "exhausted" and put in a penalty box (cooldown).
     - The library instantly switches to the next available key.
     - The request is retried automatically.
   - If all keys are exhausted, it will raise an exception (or wait, depending on future config).

## ⚠️ Disclaimer

This library is intended for legitimate use cases where you have multiple valid API keys (e.g., different projects, organization tiers) and want to ensure high availability. Please respect Google's [Terms of Service](https://ai.google.dev/terms) and API usage policies.

## 📄 License

MIT License. Feel free to use and modify!
