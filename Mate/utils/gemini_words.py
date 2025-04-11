import os
import google.generativeai as genai
from dotenv import load_dotenv
from models.english_word import EnglishWord, WordType, WordLevel
from models.extensions import db

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def fetch_words_from_gemini():
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = """
Give me 20 English vocabulary items suitable for learners preparing for the IELTS exam.
The words should be at A2, B1, or B2 CEFR levels (pre-intermediate to upper-intermediate), avoiding highly advanced or academic vocabulary.
Each item must be returned in raw JSON format with the following fields:
- "word": the English word
- "translation": its meaning in Persian
- "type": one of [noun, verb, adjective, adverb, preposition, conjunction, pronoun, other]
- "level": the CEFR level (e.g., "A2", "B1", or "B2")
- "note": (optional) a usage note or example sentence

Only return raw JSON. Do not include any explanation or description.
    """

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        word_list = eval(raw_text)

        # Process and validate words
        processed_words = []
        for item in word_list:
            word = item['word'].strip()
            translation = item['translation'].strip()
            note = item.get('note')
            type_str = item.get('type', 'other').lower()
            level_str = item.get('level', 'B1').upper()

            try:
                level = WordLevel(level_str)
            except ValueError:
                level = WordLevel.B1

            try:
                word_type = WordType(type_str)
            except ValueError:
                word_type = WordType.OTHER

            # Check if word already exists
            if not EnglishWord.query.filter_by(word=word).first():
                processed_words.append({
                    'word': word,
                    'translation': translation,
                    'type': word_type.value,
                    'level': level.value,
                    'note': note
                })

        return processed_words

    except Exception as e:
        print("⚠️ Error while fetching words:", e)
        return None
