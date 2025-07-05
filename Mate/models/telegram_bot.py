from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from .extensions import db

class TelegramUser(db.Model):
    __tablename__ = 'telegram_users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(64))
    first_name = Column(String(64))
    last_name = Column(String(64))
    registered_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TelegramUser {self.user_id} - {self.username}>"
