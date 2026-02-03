import os
import httpx
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from App.handlers import LLMServiceError

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE_PATH)

AZURE_ENDPOINT = 'https://api.kadal.ai/proxy/api/v1/azure'
LM_KEY = os.getenv("LLM_API_KEY")
API_VERSION = "2024-02-15-preview"

# Check if the key exists, with a helpful debug message if it fails
if not LM_KEY:
    raise RuntimeError(
        f"LLM_API_KEY is missing. \n"
        f"Attempted to load .env from: {ENV_FILE_PATH}\n"
        f"Please check if the file exists and contains LLM_API_KEY=your_key"
    )

client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_version=API_VERSION,
    api_key=LM_KEY,
    timeout=30.0,
    max_retries=3
)

async def get_chat_completion(messages, model="gpt-4o-mini", temperature=0.7):
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        content = response.choices[0].message.content
        
        # Log content for debugging (optional)
        print(f"LLM Response: {content}")
        
        if not content:
            raise LLMServiceError("LLM returned an empty response.")
        return content
    except Exception as e:
        error_msg = f"Kadal API Error: {str(e)}"
        raise LLMServiceError(error_msg)