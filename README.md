# Socratic CS Debugging Tutor

A curriculum-aligned AI study assistant built for high school Computer Science students learning **Java** and **Python**. Rather than acting as an answer generator, this tool uses **system-level pedagogical guardrails** and **structured JSON schemas** to guide students through debugging their own logic step by step.

## AI Engineering Highlights
- **Pedagogical Guardrails:** Enforces strict system instructions preventing the model from outputting completed homework code or bypassing the learning process.
- **Structured Outputs (Pydantic + JSON Schema):** Guarantees deterministic, machine-readable responses (`concept_identified`, `diagnosis_summary`, `socratic_question`, `next_step_hint`) suitable for LMS or classroom UI integration.
- **Low-Temperature Inference (`0.3`):** Minimizes hallucination and keeps debugging hints tightly aligned to introductory CS standards.
- **Offline Demo Mode (`--demo`):** Allows educators and reviewers to test the structured output pipeline without requiring live API credentials.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/AmyLott/socratic-cs-tutor.git](https://github.com/AmyLott/socratic-cs-tutor.git)
   cd socratic-cs-tutor
