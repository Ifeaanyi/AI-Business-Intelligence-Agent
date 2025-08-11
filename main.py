import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq  # Correct import from langchain-groq
from pydantic import BaseModel

# Load environment variables from .env
load_dotenv()

# Check if API key is loaded
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")

print(f"Groq API key loaded: {groq_api_key[:10]}...")  # Print first 10 chars to verify

try:
    # Initialize Groq with LLaMA 3 model
    llm = ChatGroq(
        model="llama3-8b-8192",  # Updated parameter name (model instead of model_name)
        groq_api_key=groq_api_key,  # Explicitly pass the API key
        temperature=0.7,  # Optional: control randomness
        max_tokens=1000   # Optional: limit response length
    )
    
    # Example prompt
    response = llm.invoke("What model are you? are you the best llm free for sql database ai agent")
    print("\nResponse:")
    print(response.content)
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting steps:")
    print("1. Verify your Groq API key in the .env file")
    print("2. Check that the variable name is exactly 'GROQ_API_KEY'")
    print("3. Ensure your API key is valid")
    print("4. Make sure you have langchain-groq installed: pip install langchain-groq")