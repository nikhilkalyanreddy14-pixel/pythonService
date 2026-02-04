import os
from pathlib import Path
from openai import AsyncAzureOpenAI
from App.handlers import LLMServiceError

# --- DIAGNOSTIC LOADER ---
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

print(f"\n--- DIAGNOSTIC START ---")
print(f"Checking Directory: {BASE_DIR}")

# 1. List all files in the directory to see if there's a sneaky .env.txt
files = os.listdir(BASE_DIR)
print(f"Files found in root: {files}")

# 2. Try to force read whatever .env file is there
if ENV_FILE_PATH.exists():
    try:
        with open(ENV_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"File '.env' opened. Total lines: {len(lines)}")
            for line in lines:
                clean_line = line.strip()
                if "LLM_API_KEY" in clean_line:
                    key = clean_line.split("=", 1)[1].strip().strip("'").strip('"')
                    os.environ["LLM_API_KEY"] = key
                    print("SUCCESS: LLM_API_KEY found and loaded into memory.")
                    break
    except Exception as e:
        print(f"READ ERROR: Could not read file contents: {e}")
else:
    print("CRITICAL: .env file does not exist at the calculated path.")

LM_KEY = os.getenv("LLM_API_KEY")
print(f"--- DIAGNOSTIC END ---\n")

if not LM_KEY:
    raise RuntimeError("Key still missing after diagnostic. Check the console output above.")

# --- REST OF YOUR CODE ---
AZURE_ENDPOINT = 'https://api.kadal.ai/proxy/api/v1/azure'
API_VERSION = "2024-02-15-preview"

client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_version=API_VERSION,
    api_key=LM_KEY,
    timeout=30.0,
    max_retries=3
)
# ... keep the rest of your get_chat_completion function ...

async def get_chat_completion(messages, model="gpt-4o-mini", temperature=0.7):
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        content = response.choices[0].message.content
        print(content)
        if not content:
            raise LLMServiceError("LLM returned an empty response.")
        return content
    except Exception as e:
        error_msg = f"Kadal API Error: {str(e)}"
        raise LLMServiceError(error_msg)