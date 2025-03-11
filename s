from app import db
from models import User
new_user = User(username="saeed", email="saeedzarbi95@gmail.com")
new_user.set_password("@#Saeed1374@#") 
db.session.add(new_user)
db.session.commit()
