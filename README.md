# MyAgents Project

This project demonstrates how one can interact with and compare different large language models (LLMs).

## Overview

- **first_agent.py**: Starts by testing a single model API (Anthropic Claude) to ensure the environment and API setup work correctly.
- **comparellm.py**: Compares the responses of several LLMs to a challenging question and judges their answers. The results are saved in `comparellms.md`.
- **resourcesandtools.py**: Module for managing external resources and tools that can be used by agents or LLMs.
- **comparellms.md**: Contains the question, the answers from each model, and the ranking of those answers.

## Models Compared and Judged

- Claude 3 Sonnet (`claude-3-7-sonnet-latest`)
- Claude 3.5 Sonnet (`claude-3-5-sonnet-20240620`)
- Mistral Small 3.1 (`mistral-small3.1:latest` via Ollama)

In comparellms.py, the answers from each model are anonymously judged by Claude Sonnet 4. This makes it possible to evaluate and compare the performance of different LLMs on the same question. 

## Chatting with a Resume or Professional Profile Using Claude 4

`resourcesandtools.py` demonstrates how to use an llm to interact with a resume (e.g., `GustaveResume - June 2025.pdf` in the `profile/` folder). The workflow involves:

1. Loading the resume or summary from the `profile/` directory.
2. Using Claude 4 to answer questions or chat about the resume content.
3. Integrating resources and LLMs to create a seamless workflow for intelligent document interaction.

This approach shows how to combine LLM capabilities with external resources to build practical AI-powered agents.
