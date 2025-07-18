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

# Gradio interface for interacting with profile and summary using Claude Sonnet 4
def chat_with_gustave(message):
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        system=system_prompt,
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
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your question")
    send_btn = gr.Button("Send")

    def respond(user_message, chat_history):
        bot_reply = chat_with_gustave(user_message)
        chat_history = chat_history + [(user_message, bot_reply)]
        return "", chat_history

    send_btn.click(respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
demo.launch()

