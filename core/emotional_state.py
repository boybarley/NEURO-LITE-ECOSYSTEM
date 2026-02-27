import re
import logging
from enum import Enum
from typing import Tuple

logger = logging.getLogger(__name__)

class EmotionalState(Enum):
    NEUTRAL = "neutral"
    CONCERNED = "concerned"
    CELEBRATORY = "celebratory"
    FRUSTRATED = "frustrated"

class EmotionalAnalyzer:
    """
    Lightweight Regex-based Emotional Classifier.
    NO ML model. < 1ms execution time.
    """
    
    # Patterns optimized for technical support contexts
    PATTERNS = {
        EmotionalState.CONCERNED: [
            r'\b(error|fail|cannot|can\'t|not working|broken|issue|problem|help|stuck|unable)\b',
            r'\b(lost|missing|afraid|worried|bad|terrible|sorry)\b'
        ],
        EmotionalState.FRUSTRATED: [
            r'\b(again|repeatedly|stupid|hate|annoying|slow|useless|wtf|why|over and over)\b',
            r'(!){2,}|\?{2,}'
        ],
        EmotionalState.CELEBRATORY: [
            r'\b(thanks|thank you|solved|works|working|great|awesome|excellent|perfect|finally|appreciate)\b',
            r'\b(success|congrats|congratulations|happy|glad)\b'
        ]
    }

    def __init__(self):
        # Pre-compile regex for performance
        self.compiled_patterns = {
            state: [re.compile(p, re.IGNORECASE) for p in patterns]
            for state, patterns in self.PATTERNS.items()
        }

    def analyze(self, text: str) -> Tuple[EmotionalState, str]:
        """
        Returns state and a system prompt modifier.
        """
        if not text:
            return EmotionalState.NEUTRAL, "Respond professionally."

        scores = {state: 0 for state in EmotionalState}
        
        for state, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                scores[state] += len(matches)

        # Determine winner
        # Default to Neutral if tie or no matches
        max_state = max(scores, key=scores.get)
        
        if scores[max_state] == 0:
            max_state = EmotionalState.NEUTRAL

        modifier = self._get_persona_modifier(max_state)
        logger.debug(f"Emotion detected: {max_state} for text: {text[:50]}...")
        return max_state, modifier

    def _get_persona_modifier(self, state: EmotionalState) -> str:
        mapping = {
            EmotionalState.NEUTRAL: "Respond professionally and concisely.",
            EmotionalState.CONCERNED: "Respond calmly and reassuringly. Prioritize a solution.",
            EmotionalState.FRUSTRATED: "Respond with patience and directness. Acknowledge the frustration.",
            EmotionalState.CELEBRATORY: "Respond warmly and professionally. Maintain the positive tone."
        }
        return mapping[state]
