import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def translate_farsi_to_english_and_turkish(farsi_sentence):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f'''
    Translate the following Persian sentence to both English and Turkish:
    "{farsi_sentence}"
    Return the result in this JSON format:
    {{
        "english": "...",
        "turkish": "..."
    }}
    Only return raw JSON, no explanation.
    '''
    response = model.generate_content(prompt)
    import json
    raw = response.text.strip()
    if raw.startswith("```json"):
        raw = raw.replace("```json", "").replace("```", "").strip()
    result = json.loads(raw)
    return result