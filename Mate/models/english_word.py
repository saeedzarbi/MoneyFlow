from persiantools.jdatetime import JalaliDateTime
from datetime import datetime
import pytz
from .extensions import db
from enum import Enum
from flask_login import UserMixin

class WordLevel(Enum):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'

class WordType(Enum):
    NOUN = 'noun'
    VERB = 'verb'
    ADJECTIVE = 'adjective'
    ADVERB = 'adverb'
    PREPOSITION = 'preposition'
    CONJUNCTION = 'conjunction'
    PRONOUN = 'pronoun'
    OTHER = 'other'

class EnglishWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    translation = db.Column(db.String(200), nullable=False)
    type = db.Column(db.Enum(WordType), nullable=False)
    level = db.Column(db.Enum(WordLevel), nullable=False) 
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('Asia/Tehran')))

    def __init__(self, word, translation, type, level, note=None):
        self.word = word
        self.translation = translation
        self.type = type
        self.level = level
        self.note = note
        self.created_at = datetime.now(pytz.timezone('Asia/Tehran'))

    def get_persian_date(self):
        return JalaliDateTime(self.created_at).strftime('%Y/%m/%d')

    def __repr__(self):
        return f"<EnglishWord {self.word} - {self.translation} ({self.level.value})>"

class WordSentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.Text, nullable=False)  
    translation = db.Column(db.Text, nullable=False) 
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('Asia/Tehran')))
    english_word_id = db.Column(db.Integer, db.ForeignKey('english_word.id'), nullable=False)
    
    english_word = db.relationship('EnglishWord', backref=db.backref('sentences', lazy=True, cascade='all, delete-orphan'))

    def __init__(self, sentence, translation, english_word_id):
        self.sentence = sentence
        self.translation = translation
        self.english_word_id = english_word_id
        self.created_at = datetime.now(pytz.timezone('Asia/Tehran'))

    def get_persian_date(self):
        return JalaliDateTime(self.created_at).strftime('%Y/%m/%d')

    def __repr__(self):
        return f"<WordSentence {self.sentence[:30]}...>" 