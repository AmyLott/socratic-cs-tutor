import os
import json
import argparse
from pydantic import BaseModel, Field

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


# 1. Structured Output Schema (Ensures predictable, parseable AI responses)
class TutorResponse(BaseModel):
    concept_identified: str = Field(
        description="The core CS concept involved (e.g., Off-by-one loop error, Variable scope, Integer division)."
    )
    diagnosis_summary: str = Field(
        description="Brief, encouraging explanation of what the code is currently doing without giving the fix."
    )
    socratic_question: str = Field(
        description="One targeted question guiding the student to spot and fix the logic bug themselves."
    )
    next_step_hint: str = Field(
        description="A small, concrete debugging action (e.g., 'Trace the value of i on the final loop iteration')."
    )


# 2. System Prompt & Pedagogical Guardrails
SYSTEM_INSTRUCTION = """
You are a patient, encouraging high school Computer Science tutor specializing in beginner Java and Python.

STRICT PEDAGOGICAL GUARDRAILS:
1. NEVER write, complete, or output corrected code blocks for the student's assignment.
2. NEVER give away the direct answer, even if the student asks you to "just fix it" or claims they are out of time.
3. Identify ONLY the single highest-priority logic or syntax issue first so the student is not overwhelmed.
4. Use Socratic questioning: help the student trace their own variables, loop bounds, or conditionals.
5. Keep explanations clear, concise, and accessible for first-time programmers.
"""


def get_demo_response(student_code: str) -> TutorResponse:
    """Provides a deterministic sample response when running without an API key."""
    return TutorResponse(
        concept_identified="Loop Boundary / Off-by-One Error (ArrayIndexOutOfBounds)",
        diagnosis_summary=(
            "Your loop starts at index 0 and continues while i <= scores.length. "
            "Remember that in zero-indexed arrays, the last valid index is always one less than the total length."
        ),
        socratic_question=(
            "If an array has 5 elements (indices 0 through 4), what happens when i reaches 5 "
            "and your code tries to access scores[5]?"
        ),
        next_step_hint="Check the comparison operator (<= vs <) in your for-loop condition."
    )


def analyze_student_code(language: str, student_code: str, student_question: str, demo: bool = False) -> TutorResponse:
    """Sends student code to the LLM with system guardrails and structured JSON schema."""
    if demo:
        return get_demo_response(student_code)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable not set. "
            "Set it via 'export GEMINI_API_KEY=your_key' or run with --demo."
        )

    if genai is None:
        raise ImportError("google-genai package not installed. Run: pip install -r requirements.txt")

    client = genai.Client(api_key=api_key)

    user_prompt = f"""
    Language: {language}
    Student's Question: {student_question}

    Student's Code:
    ```
    {student_code}
    ```
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=TutorResponse,
            temperature=0.3,  # Low temperature for consistent, reliable pedagogical guardrails
        ),
    )

    data = json.loads(response.text)
    return TutorResponse(**data)


def main():
    parser = argparse.ArgumentParser(description="Curriculum-Aligned Socratic CS Debugging Tutor")
    parser.add_argument("--lang", default="Java", help="Programming language (Java or Python)")
    parser.add_argument("--demo", action="store_true", help="Run in offline demo mode without an API key")
    args = parser.parse_args()

    print("=== Socratic CS Debugging Tutor ===")
    print(f"Active Language Track: {args.lang} | Guardrails: ENFORCED\n")

    if args.demo:
        sample_code = """int[] scores = {88, 92, 79, 95, 84};
int sum = 0;
for (int i = 0; i <= scores.length; i++) {
    sum += scores[i];
}"""
        sample_question = "Why am I getting an ArrayIndexOutOfBoundsException?"
        print(f"Sample Student Question: {sample_question}")
        print(f"Sample Code:\n{sample_code}\n")
        result = analyze_student_code(args.lang, sample_code, sample_question, demo=True)
    else:
        question = input("What error or issue are you running into? ")
        print("Paste your code below (type 'END' on a new line when finished):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        code = "\n".join(lines)
        result = analyze_student_code(args.lang, code, question, demo=False)

    print("--- Structured Tutor Guidance ---")
    print(f"Core Concept     : {result.concept_identified}")
    print(f"What's Happening : {result.diagnosis_summary}")
    print(f"Think About This : {result.socratic_question}")
    print(f"Next Debug Step  : {result.next_step_hint}")


if __name__ == "__main__":
    main()
