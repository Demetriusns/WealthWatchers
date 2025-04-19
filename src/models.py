from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    #id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), nullable=False)    
    firstname = db.Column(db.String(20)) 
    lastname = db.Column(db.String(20)) 

    # def get_id(self):
    #     return str(self.email)
    
    def __init__(self, email):
        self.email = email  

    def get_id(self):
        return str(self.user_id)

class Register(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname= db.Column(db.String(20))    
    lastname = db.Column(db.String(20))  
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)    

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    category = db.Column(db.String(100))
    date = db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
