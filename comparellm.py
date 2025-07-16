from dotenv import load_dotenv
from anthropic import Anthropic
import os

# Add OpenAI client for Ollama
from openai import OpenAI

load_dotenv(override=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("API_KEY is not set in the environment variables.")

anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# OpenAI client for Ollama (local models)
ollama_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def main():
    # Step 1: Get a challenging question from claude-3-7-sonnet-latest
    question_response = anthropic_client.messages.create(
        model="claude-3-7-sonnet-latest",
        max_tokens=500,
        messages=[
            {"role": "user", "content": "Please come up with a challenging, "
            "nuanced question that I can ask a number of LLM models to evaluate their intelligence. Answer only with the question"},
        ],
    )
    question = question_response.content[0].text.strip()

    # Step 2: Get answer from claude-3-7-sonnet-latest
    answerby_37_response = anthropic_client.messages.create(
        model="claude-3-7-sonnet-latest",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": question},
        ],
    )
    answerby_37 = answerby_37_response.content[0].text.strip()

    # Step 3: Get answer from claude-3-5-sonnet-20240620
    answerby_35_response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": question},
        ],
    )
    answerby_35 = answerby_35_response.content[0].text.strip()

    # Step 3.5: Get answer from mistral-small3.1:latest via Ollama
    mistral_response = ollama_client.chat.completions.create(
        model="mistral-small3.1:latest",
        messages=[
            {"role": "user", "content": question},
        ],
        max_tokens=1000,
    )
    answerby_mistral_small31 = mistral_response.choices[0].message.content.strip()

    # Step 4: Save results in markdown file with model names as headings
    model_names = [
        "Claude 3 Sonnet (claude-3-7-sonnet-latest)",
        "Claude 3.5 Sonnet (claude-3-5-sonnet-20240620)",
        "Mistral Small 3.1 (mistral-small3.1:latest via Ollama)"
    ]
    answers = [answerby_37, answerby_35, answerby_mistral_small31]
    markdown = f"""
# Challenging Question

{question}
"""
    for idx, (model, answer) in enumerate(zip(model_names, answers), 1):
        markdown += f"""

---

## {model}

{answer}
"""

    # Step 5: Judge the answers anonymously, then map ranking to model names
    judging_prompt = (
        "You are an impartial judge. Here is a challenging question and three answers from different AI models. "
        "The answers are anonymized and labeled as Answer 1, Answer 2, and Answer 3. "
        "Please rank the answers from best to worst in terms of correctness, depth, clarity, and insight. "
        "Return ONLY a JSON array of the answer numbers in ranked order, e.g. [2, 1, 3]. Do not include any explanation or extra text.\n\n"
        f"Question:\n{question}\n\n"
        f"Answer 1:\n{answers[0]}\n\n"
        f"Answer 2:\n{answers[1]}\n\n"
        f"Answer 3:\n{answers[2]}\n"
    )
    ranking_response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[
            {"role": "user", "content": judging_prompt},
        ],
    )
    ranking_json = ranking_response.content[0].text.strip()

    # Try to parse the ranking JSON to map to model names
    import json
    try:
        ranking_list = json.loads(ranking_json)
        if isinstance(ranking_list, list) and all(isinstance(x, int) for x in ranking_list):
            ranked_models = [model_names[i-1] for i in ranking_list]
        else:
            ranked_models = None
    except Exception:
        ranked_models = None

    markdown += f"""

---

## Ranking (by Claude Sonnet 4)

```json
{ranking_json}
```
"""
    if ranked_models:
        markdown += "\n**Ranking by model name:**\n\n"
        for idx, model in enumerate(ranked_models, 1):
            markdown += f"{idx}. {model}\n"

    with open("comparellms.md", "w", encoding="utf-8") as f:
        f.write(markdown)

if __name__ == "__main__":
    main()