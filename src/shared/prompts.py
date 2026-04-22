SYSTEM_MESSAGE = (
    "You are an educational content creator. Output pure JSON only."
)

BASE_PROMPT_TEMPLATE = """
Generate educational questions in JSON format.
Subject: {subject}
Grade: {grade}
Language: {medium}

Content Source:
"{content}"
"""

PHYSICS_INSTRUCTIONS = """
Requirements (PHYSICS):
- Include physics calculations and conceptual depth.
- Write Math/Physics expressions in LaTeX inside $ signs
  (e.g. $9.8 m/s^2$).
"""

GENERAL_INSTRUCTIONS = """
Requirements:
- Create varied questions covering all concepts.
"""

COMMON_INSTRUCTIONS = """
Output pure JSON object strictly following this structure:
{
  "questions": [
    {
      "type": "mcq", // or "fill_in_the_blank" or "structured"
      "question_text": "text here... (for fill blanks use {0}, {1})",
      "options": ["A", "B", "C", "D"], // options (empty for structured)
      "answer": ["A"], // list of correct options or words
      "explanation": "Detailed explanation..."
    }
  ]
}
Generate around 5-10 high-quality questions. Return only JSON.
"""
