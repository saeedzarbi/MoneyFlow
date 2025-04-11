#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gemini_words import fetch_words_from_gemini
from app import create_app
from models.extensions import db
from models.english_word import EnglishWord

def main():
    print("🔄 Fetching words from Gemini...")
    app = create_app()
    with app.app_context():
        try:
            # Create database tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Fetch and save words
            fetch_words_from_gemini()
            print("✅ Done!")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()