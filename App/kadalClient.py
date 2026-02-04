import os
import httpx
import json
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
    
LLM_GATEWAY_URL = 'https://api.kadal.ai/proxy/api/v1'

async def run_gpt(messages):
    clientC = AsyncAzureOpenAI(
        azure_endpoint=f"{LLM_GATEWAY_URL}/azure",
        api_version=API_VERSION,
        api_key=LM_KEY
    )
    print("GPT Response\n")
    try:
        response = await clientC.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        content = response.choices[0].message.content
        print(content)
        if not content:
            raise LLMServiceError("LLM returned an empty response.")
        return content
    except Exception as e:
        errorMsg = f"kadal api error: {str(e)}"
        raise LLMServiceError(errorMsg)
    
async def run_gemini(messages):
    MODEL_NAME = 'gemini-1.5-pro'
    url = f"{LLM_GATEWAY_URL}/gemini/models/{MODEL_NAME}:generateContent"
    
    gemini_contents = []
    for msg in messages:
        gemini_role = "model" if msg["role"] == "assistant" else "user"
        gemini_contents.append({
            "role": gemini_role,
            "parts": [{"text": msg["content"]}]
        })

    headers = {
        "Content-Type": "application/json",
        "api-key": f"{LM_KEY}"
    }
    
    data = {"contents": gemini_contents}
    print("Gemini Request (Async with verify=True)")

    try:
        async with httpx.AsyncClient(verify=True) as client_async:
            response = await client_async.post(
                url, 
                headers=headers, 
                json=data, 
                timeout=60.0
            )
        
        response.raise_for_status()
        result = response.json()

        # --- FIX START ---
        # If the API returns a stringified JSON, parse it again
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except:
                pass 
        
        # Check if it's a dictionary before accessing keys
        if isinstance(result, dict) and 'candidates' in result:
            answer = result['candidates'][0]['content']['parts'][0]['text']
            print(answer)
            return answer
        else:
            # Helpful debug: what did we actually get?
            print(f"DEBUG: Unexpected result type: {type(result)}")
            print(f"DEBUG: Content: {result}")
            raise LLMServiceError(f"Invalid Gemini response structure. See logs.")
        # --- FIX END ---

    except httpx.HTTPStatusError as e:
        raise LLMServiceError(f"API Error ({e.response.status_code}): {e.response.text}")
    except Exception as e:
        # Re-raising with the specific error to find the root cause
        raise LLMServiceError(f"Kadal Gemini Error: {str(e)}")