import random
import time
from typing import List, Optional

class KeyManager:
    def __init__(self, api_keys: List[str], strategy: str = "round_robin"):
        """
        Initialize the KeyManager.
        
        :param api_keys: List of Gemini API keys.
        :param strategy: Strategy for key selection ('round_robin' or 'random').
        """
        if not api_keys:
            raise ValueError("API keys list cannot be empty.")
        
        self.api_keys = api_keys
        self.strategy = strategy
        self.current_index = 0
        self.exhausted_keys = {}  # Map of key -> timestamp when it was exhausted
        self.cooldown_seconds = 60  # Simple cooldown for exhausted keys

    def get_key(self) -> str:
        """Returns a valid API key based on the strategy."""
        valid_keys = [k for k in self.api_keys if not self._is_exhausted(k)]
        
        if not valid_keys:
            # If all keys are exhausted, wait for the one with the earliest expiry
            # Or just raise an exception. For now, let's reset if all are exhausted 
            # (assuming some time passed) or pick the one that expires soonest.
            # A simple approach: just pick one and hope for the best, or raise error.
            # Let's try to pick the one that was exhausted longest ago.
            if self.exhausted_keys:
                oldest_exhausted = min(self.exhausted_keys, key=self.exhausted_keys.get)
                return oldest_exhausted
            return self.api_keys[0] # Fallback

        if self.strategy == "random":
            return random.choice(valid_keys)
        else:  # round_robin
            # Find next valid key starting from current_index
            for _ in range(len(self.api_keys)):
                key = self.api_keys[self.current_index]
                self.current_index = (self.current_index + 1) % len(self.api_keys)
                if key in valid_keys:
                    return key
            
            return valid_keys[0]

    def report_exhausted(self, key: str):
        """Mark a key as exhausted."""
        print(f"Key ...{key[-4:]} exhausted. Switching...")
        self.exhausted_keys[key] = time.time()

    def _is_exhausted(self, key: str) -> bool:
        """Check if a key is currently in cooldown."""
        if key not in self.exhausted_keys:
            return False
        
        exhausted_time = self.exhausted_keys[key]
        if time.time() - exhausted_time > self.cooldown_seconds:
            del self.exhausted_keys[key]
            return False
        return True
