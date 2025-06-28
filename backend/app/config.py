# Configuration settings
import os

LOCAL_LLM_MODEL = "qwen3:0.6b"
VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db_data")
COLLECTION_NAME = "got_ai_knowledge"

# Archive settings
ARCHIVE_BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "archive")

# The Interrogative Battery
INTERROGATIVE_BATTERY = [
    "Why is this the case?", 
    "What are the underlying assumptions?", 
    "How can this be explained differently?", 
    "What is the primary consequence of this?", 
    "Where would this have the biggest impact?"
]

# Prompts
AGENT_PROMPT_TEMPLATE = """
You are a creative and logical thinker. Given the following statement, generate a concise, one-sentence outcome for the question: "{question}"

Statement: "{statement_text}"

Your one-sentence outcome:
"""

LOGIC_SCORING_PROMPT_TEMPLATE = """
On a scale from 0.0 to 1.0, how logically sound and internally consistent is the following statement? Output ONLY the number.

Statement: "{text}"

Score:
"""

PLAUSIBILITY_SEARCH_PROMPT_TEMPLATE = """
Generate a concise search query to verify the following statement. Output only the search query, no explanation.

Statement: "{text}"

Search query:
"""

PLAUSIBILITY_VERIFICATION_PROMPT_TEMPLATE = """
Based on the search results below, rate how plausible the given statement is on a scale from 0.0 to 1.0. Output ONLY the number.

Statement: "{text}"

Search Results:
{search_results}

Plausibility score:
"""
