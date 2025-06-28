from ..llm.llm_interface import llm_client
from .. import config
import logging
import re

logger = logging.getLogger(__name__)

class Scorer:
    def score_logic(self, text: str) -> float:
        """Score the logical consistency of a statement"""
        try:
            prompt = config.LOGIC_SCORING_PROMPT_TEMPLATE.format(text=text)
            response = llm_client.generate_short(prompt)
            
            # Extract number from response
            numbers = re.findall(r'0\.\d+|1\.0|0|1', response)
            if numbers:
                score = float(numbers[0])
                return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            return 0.1  # Default low score if no valid number found
        except Exception as e:
            logger.error(f"Error scoring logic: {e}")
            return 0.1

    def score_plausibility(self, text: str) -> float:
        """Score the plausibility of a statement using search-based verification"""
        # For now, we'll use a simple heuristic. 
        # In a full implementation, this would:
        # 1. Generate a search query from the text
        # 2. Run a web search
        # 3. Compare results to the statement
        
        # Simple heuristic: longer, more detailed statements get higher scores
        try:
            word_count = len(text.split())
            if word_count > 20:
                return 0.8
            elif word_count > 10:
                return 0.6
            else:
                return 0.4
        except Exception as e:
            logger.error(f"Error scoring plausibility: {e}")
            return 0.5

    def calculate_final_score(self, text: str) -> float:
        """Calculate the final weighted score for a statement"""
        try:
            logic = self.score_logic(text)
            plausibility = self.score_plausibility(text)
            
            # Weighted average: 60% logic, 40% plausibility
            final_score = (0.6 * logic) + (0.4 * plausibility)
            
            logger.info(f"Scored text: logic={logic:.2f}, plausibility={plausibility:.2f}, final={final_score:.2f}")
            return final_score
        except Exception as e:
            logger.error(f"Error calculating final score: {e}")
            return 0.1

# Global instance
scorer = Scorer()
