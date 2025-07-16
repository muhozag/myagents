from dotenv import load_dotenv
from anthropic import Anthropic
import os

load_dotenv(override=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("API_KEY is not set in the environment variables.")

anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

def main():
    response = anthropic_client.messages.create(
        model="claude-3-7-sonnet-latest",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": "Hello, what is 2+5?"},
        ],
        system="You are a helpful assistant."
    )
    print(response.content[0].text)

if __name__ == "__main__":
    main()



