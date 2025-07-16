# MyAgents Project

This project demonstrates how one can interact with and compare different large language models (LLMs).

## Overview

- **first_agent.py**: Starts by testing a single model API (Anthropic Claude) to ensure the environment and API setup work correctly.
- **comparellm.py**: Compares the responses of several LLMs to a challenging question and judges their answers. The results are saved in `comparellms.md`.
- **comparellms.md**: Contains the question, the answers from each model, and the ranking of those answers.

## Models Compared and Judged

- Claude 3 Sonnet (`claude-3-7-sonnet-latest`)
- Claude 3.5 Sonnet (`claude-3-5-sonnet-20240620`)
- Mistral Small 3.1 (`mistral-small3.1:latest` via Ollama)

This setup allows you to evaluate and compare the performance of different LLMs on the same question.
