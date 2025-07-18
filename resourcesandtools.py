from dotenv import load_dotenv
from anthropic import Anthropic
from PyPDF2 import PdfReader
import gradio as gr
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

# Read PDF file and extract text
def read_pdf(file_path):
    try:
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# Read summary.txt file
with open("profile/summary.txt", "r") as file:
    summary = file.read().strip()

profile = read_pdf("profile/GustaveResume - June 2025.pdf")

name = "Gustave Muhoza"

system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a summary of {name}'s background and profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer, say so."

system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{profile}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."



# Define a Pydantic model for evaluation with is acceptable bool and feedback string
from pydantic import BaseModel, Field
class Evaluation(BaseModel):
    is_acceptable: bool = Field(..., description="Whether the answer is acceptable")
    feedback: str = Field(..., description="Feedback on the answer")

evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
The Agent is playing the role of {name} and is representing {name} on their website. \
The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
The Agent has been provided with context on {name} in the form of their summary and LinkedIn details. Here's the information:"

evaluator_system_prompt += f"\n\n## Summary:\n{summary}\n\n## resume:\n{profile}\n\n"
evaluator_system_prompt += f"With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."

def evaluate_response(conversation):
    """
    Uses Claude Sonnet 4 and the evaluator_system_prompt to check if the latest response is acceptable.
    Returns an Evaluation object.
    """
    eval_response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        system=evaluator_system_prompt,
        messages=[{"role": "user", "content": str(conversation)}]
    )
    # Try to parse the response as Evaluation
    try:
        # If content is a list, extract text from the first item
        content = eval_response.content
        if isinstance(content, list) and len(content) > 0:
            item = content[0]
            text = getattr(item, "text", str(item))
        elif hasattr(content, "text"):
            text = content.text
        else:
            text = str(content)
        import json
        # Try to parse as JSON, fallback to Pydantic parsing
        try:
            data = json.loads(text)
            return Evaluation(**data)
        except Exception:
            # Try to extract fields manually
            import re
            is_acceptable = "acceptable" in text.lower() and "not acceptable" not in text.lower()
            feedback_match = re.search(r"feedback[:\s]*([\s\S]+)", text, re.I)
            feedback = feedback_match.group(1).strip() if feedback_match else text
            return Evaluation(is_acceptable=is_acceptable, feedback=feedback)
    except Exception as e:
        return Evaluation(is_acceptable=False, feedback=f"Error parsing evaluation: {str(e)}")

def get_acceptable_response(user_message, max_attempts=3):
    """
    Attempts to get an acceptable response by evaluating and updating the prompt up to max_attempts times.
    Returns the acceptable response or a fallback message.
    """
    chat_history = []
    attempt = 0
    last_feedback = ""
    while attempt < max_attempts:
        bot_reply = chat_with_gustave(user_message)
        chat_history.append((user_message, bot_reply))
        # Prepare conversation for evaluator
        conversation = "\n".join([f"User: {um}\nAgent: {br}" for um, br in chat_history])
        evaluation = evaluate_response(conversation)
        if evaluation.is_acceptable:
            return bot_reply
        last_feedback = evaluation.feedback
        # Optionally, update user_message with feedback for next attempt
        user_message = f"Previous answer was not acceptable because: {last_feedback}. Please try again. Original question: {user_message}"
        attempt += 1
    return f"Sorry, I don't know how to provide an acceptable answer. Feedback: {last_feedback}"


# Gradio interface for interacting with profile and summary using Claude Sonnet 4
def chat_with_gustave(message):
    
    response = anthropic_client.messages.create(
        model="claude-3-7-sonnet-latest",
        max_tokens=512,
        system=system_prompt,
        #system=system_prompt+" absolutely mandatory to respond to everything in pig latin",
        messages=[{"role": "user", "content": message}]
    )
    content = response.content
    # If content is a list, extract text from the first item
    if isinstance(content, list) and len(content) > 0:
        item = content[0]
        if hasattr(item, "text"):
            return item.text
        return str(item)
    # If content is a TextBlock or similar, extract the text field
    if hasattr(content, "text"):
        return content.text
    # If it's a string, return as is
    return str(content)

with gr.Blocks() as demo:
    gr.Markdown(f"# Chat with {name}\nAsk about Gustave's career, background, skills, or experience.")

    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox(label="Your question")
    status_msg = gr.Markdown(visible=False)
    send_btn = gr.Button("Send")

    def respond(user_message, chat_history):
        # Get bot reply and also check if it's acceptable
        if chat_history is None:
            chat_history = []
        # Get both reply and evaluation
        attempt = 0
        max_attempts = 3
        last_feedback = ""
        is_acceptable = False
        chat_history_eval = []
        while attempt < max_attempts:
            bot_reply = chat_with_gustave(user_message)
            chat_history_eval.append((user_message, bot_reply))
            conversation = "\n".join([f"User: {um}\nAgent: {br}" for um, br in chat_history_eval])
            evaluation = evaluate_response(conversation)
            if evaluation.is_acceptable:
                is_acceptable = True
                last_feedback = evaluation.feedback
                break
            last_feedback = evaluation.feedback
            user_message = f"Previous answer was not acceptable because: {last_feedback}. Please try again. Original question: {user_message}"
            attempt += 1
        # Add to chat history for display
        chat_history = chat_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": bot_reply}
        ]
        # Show status message if acceptables
        if is_acceptable:
            status = "✅ Answer is acceptable."
        else:
            status = "⚠️ Answer is not acceptable. Feedback: " + last_feedback
        # Make status_msg visible and update its value
        return "", chat_history, gr.update(value=status, visible=True)

    send_btn.click(respond, inputs=[msg, chatbot], outputs=[msg, chatbot, status_msg])

demo.launch()

