import re
import logging

logger = logging.getLogger(__name__)

class PostProcessor:
    """
    Rule-based polisher.
    Target: < 2ms.
    """

    @staticmethod
    def process(text: str, emotional_context: str) -> str:
        """
        Apply heuristics and formatting.
        """
        # 1. Trim whitespace
        text = text.strip()

        # 2. Empathy Injection (Only if missing)
        # Check if text starts with empathy markers (e.g., "I understand", "I'm sorry")
        empathy_markers = ["i understand", "i am sorry", "i apologize", "great news", "glad to hear"]
        first_sentence = text.split('.')[0].lower()
        
        has_empathy = any(marker in first_sentence for marker in empathy_markers)
        
        # Inject only if not celebratory and missing empathy
        # Note: We don't inject for 'neutral' to avoid being annoying.
        if not has_empathy:
            if "concerned" in emotional_context.lower():
                text = f"I understand the issue. {text}"
            elif "frustrated" in emotional_context.lower():
                text = f"I apologize for the inconvenience. {text}"

        # 3. Professional Formatting
        # Ensure list items have spacing
        # Convert "1.Item" to "1. Item"
        text = re.sub(r'(\d+)\.(?=[A-Z|a-z])', r'\1. ', text)
        
        # Ensure code blocks have newlines (basic heuristic)
        # If text contains code-like indentation, wrap in markdown? 
        # Skipping code wrapping to be safe, rely on LLM output.

        return text
