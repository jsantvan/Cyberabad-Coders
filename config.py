import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("🔴 GOOGLE_API_KEY not found. Please set it in your .env file.")

# Configure the Generative AI library
genai.configure(api_key=api_key)

# Create an instance of the model to be used throughout the app
model = genai.GenerativeModel('gemini-1.5-flash')

print("✅ Gemini API configured successfully.")