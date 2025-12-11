import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InternalServerError
import time
from typing import List, Any
from .key_manager import KeyManager

class GoodbyeQuota:
    def __init__(self, api_keys: List[str], strategy: str = "round_robin"):
        self.key_manager = KeyManager(api_keys, strategy)
        self.max_retries = len(api_keys) * 2  # Allow cycling through keys a few times

    def _configure_current_key(self):
        key = self.key_manager.get_key()
        genai.configure(api_key=key)
        return key

    def create_model(self, model_name: str, **kwargs):
        return QuotaFreeModel(self, model_name, **kwargs)

class QuotaFreeModel:
    def __init__(self, client: GoodbyeQuota, model_name: str, **kwargs):
        self.client = client
        self.model_name = model_name
        self.model_kwargs = kwargs
        # We don't instantiate the model here permanently because the client might change keys
        # But the model object itself in genai doesn't store the key, the global config does.
        self._model = genai.GenerativeModel(model_name, **kwargs)

    def generate_content(self, *args, **kwargs):
        retries = 0
        while retries < self.client.max_retries:
            current_key = self.client._configure_current_key()
            try:
                return self._model.generate_content(*args, **kwargs)
            except ResourceExhausted:
                self.client.key_manager.report_exhausted(current_key)
                retries += 1
                print(f"Quota exceeded for key ...{current_key[-4:]}. Retrying with new key...")
            except (ServiceUnavailable, InternalServerError):
                # Optional: handle transient errors with a simple retry without switching keys immediately
                # or switch keys just in case.
                print(f"Service error. Retrying...")
                time.sleep(1)
                retries += 1
            except Exception as e:
                raise e
        
        raise Exception("All keys exhausted or max retries reached.")

    def start_chat(self, history=None):
        return QuotaFreeChat(self, history)

class QuotaFreeChat:
    def __init__(self, model: QuotaFreeModel, history=None):
        self.model = model
        self.history = history or []
        self._chat = self.model._model.start_chat(history=self.history)

    def send_message(self, content, **kwargs):
        retries = 0
        while retries < self.model.client.max_retries:
            current_key = self.model.client._configure_current_key()
            try:
                # We need to be careful here. If we switch keys, the chat session *might* be affected 
                # if the session state is stored server-side keyed by API key?
                # Gemini API is stateless regarding the model object, but start_chat maintains history locally.
                # So it should be fine to switch keys as long as we send the history.
                # However, `_chat.send_message` updates the local history object.
                return self._chat.send_message(content, **kwargs)
            except ResourceExhausted:
                self.model.client.key_manager.report_exhausted(current_key)
                retries += 1
                print(f"Quota exceeded for key ...{current_key[-4:]}. Retrying with new key...")
            except Exception as e:
                raise e
        
        raise Exception("All keys exhausted or max retries reached.")
