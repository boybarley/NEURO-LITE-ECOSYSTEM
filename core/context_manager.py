import logging
import re
from collections import deque
from typing import List, Dict

logger = logging.getLogger(__name__)

class ContextManager:
    """
    Sliding Window Memory.
    Rules:
    1. System Prompt is persistent.
    2. Heuristic Bridge Summary (no LLM).
    """
    
    def __init__(self, max_history_tokens: int = 1024, system_prompt: str = ""):
        self.system_prompt = system_prompt
        self.history = deque() # List of {'role': str, 'content': str}
        # Approximate token limit (4 chars ~ 1 token)
        self.max_history_chars = max_history_tokens * 4
        
    def _heuristic_bridge_summary(self, old_history: List[Dict]) -> str:
        """
        Create a pseudo-summary using regex extraction.
        No LLM inference allowed.
        """
        text_block = " ".join([msg['content'] for msg in old_history])
        
        # Extract capitalized phrases or potential entities (Naive NER)
        # Look for things like "Error 503", "Database Connection", "Install.sh"
        entities = set()
        # Match CamelCase or Capitalized Phrases
        matches = re.findall(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b', text_block)
        entities.update(matches)
        
        # Match code-like terms
        code_matches = re.findall(r'\b([\w\-\_\.]+\.[\w]+)\b', text_block) # filenames
        entities.update(code_matches)

        if entities:
            # Deduplicate and format
            entity_list = list(entities)[:5] # Top 5 entities
            return f"Context summary: User previously discussed {', '.join(entity_list)}."
        
        return "Context summary: Previous conversation ended."

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        self._enforce_limits()

    def _enforce_limits(self):
        """
        Maintain sliding window.
        """
        current_len = sum(len(msg['content']) for msg in self.history)
        
        if current_len > self.max_history_chars:
            logger.info("Context limit reached. Compressing history.")
            
            # Calculate how much to remove
            # We keep the last few turns intact
            keep_recent = 2 # Last 2 exchanges (User + Assistant)
            recent_msgs = list(self.history)[-keep_recent:]
            
            # Items to be compressed
            old_msgs = list(self.history)[:-keep_recent]
            
            if old_msgs:
                bridge = self._heuristic_bridge_summary(old_msgs)
                # Reset history to bridge + recent
                self.history = deque()
                # Inject bridge as a system context
                self.history.append({"role": "system", "content": bridge})
                self.history.extend(recent_msgs)

    def get_full_context(self) -> List[Dict]:
        """
        Returns the context including system prompt.
        """
        # Prepend system prompt
        context = [{"role": "system", "content": self.system_prompt}]
        context.extend(list(self.history))
        return context

    def clear(self):
        self.history.clear()
