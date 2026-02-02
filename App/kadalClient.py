import httpx
from openai import AzureOpenAI

# Configuration constants
AZURE_ENDPOINT = 'https://api.kadal.ai/proxy/api/v1/azure'
LM_KEY = 'LM-KlRBYKcXtKbY8fi2H6yeeCaX8Sm8hC437CWF7B2pA'
API_VERSION = "2024-02-15-preview"

# SSL setup for corporate networks
unsafe_client = httpx.Client(verify=False)

# Initialize the AzureOpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_version=API_VERSION,
    api_key=LM_KEY,
    http_client=unsafe_client
)

def get_chat_completion(messages, model="gpt-4o-mini", temperature=0.7):
    """
    Core function to call the AI. 
    Corrected model name to 'gpt-4o-mini'.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        
       # print(response) 
        print("\n")
        # Get the AI's answer
        return response.choices[0].message.content
    except Exception as e:
        print(f"[KadalClient Error]: {e}")
        return ""
    
    