import requests
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
from models.english_word import WordType, WordLevel

load_dotenv()

def send_daily_words_to_slack(words):
    """
    Send daily words to Slack channel using webhook
    """
    try:
        # Get webhook URL from environment variable
        webhook_url = os.getenv('ENGLISH-SLACK')
        if not webhook_url:
            print("Error: SLACK-HOOK environment variable is not set")
            return False
        
        # Get today's date in Tehran timezone
        tehran_tz = pytz.timezone('Asia/Tehran')
        today = datetime.now(tehran_tz).strftime('%Y-%m-%d')
        
        # Create message text with beautiful header
        message_text = f"✨ *📚 Daily English Words - {today}* ✨\n"
        message_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Add each word to the message with emojis
        for i, word in enumerate(words, 1):
            # Add word number and emoji
            message_text += f"*{i}.* 🎯 *{word.word}*\n"
            
            # Add translation with emoji
            message_text += f"   📖 *Translation:* {word.translation}\n"
            
            # Add type with appropriate emoji
            type_emoji = {
                WordType.NOUN: '📝',
                WordType.VERB: '⚡',
                WordType.ADJECTIVE: '🌈',
                WordType.ADVERB: '🎭',
                WordType.PRONOUN: '💬',
                WordType.OTHER: '💬',

            }.get(word.type, '📌')
            message_text += f"   {type_emoji} *Type:* {word.type.value}\n"
            
            # Add level with appropriate emoji
            level_emoji = {
                WordLevel.A1: '🌱',
                WordLevel.A2: '🌱',
                WordLevel.B1: '🌿',
                WordLevel.C1: '🌳',
                WordLevel.B2: '🌿',
                WordLevel.C2: '🌳'
            }.get(word.level, '📊')
            message_text += f"   {level_emoji} *Level:* {word.level.value}\n"
            
            # Add note if exists
            if word.note:
                message_text += f"   💡 *Note:* {word.note}\n"
            
            # Add separator between words
            message_text += "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Add footer
        message_text += "🌟 *Keep learning and growing!* 🌟"
        
        # Prepare payload for webhook
        payload = {
            "text": message_text
        }
        
        # Send message to Slack using webhook
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error sending message to Slack: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending message to Slack: {e}")
        return False 