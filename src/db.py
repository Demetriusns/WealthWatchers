from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    create_time = db.Column(db.String(20), nullable=False)
    role = db.Column(db.Enum('Admin', 'User', name='user_roles'), nullable=False, default='User')
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f"<User {self.email}, Role: {self.role}>"

    def get_id(self):
        return str(self.user_id)

class Account(db.Model):
    __tablename__ = 'accounts'

    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bank_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.Enum('Asset', 'Liability'), nullable=False)
    balance = db.Column(db.Numeric(15, 2), nullable=False)
    create_time = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Account {self.account_id}, Bank: {self.bank_name}, Balance: {self.balance}>"


class Saving(db.Model):
    __tablename__ = 'savings'
    savings_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    date = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    description = db.Column(db.String(255), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)

    category = db.relationship('Category', backref='savings', lazy=True)
    account = db.relationship('Account', backref='savings', lazy=True)

    def __repr__(self):
        return f"<Savings {self.savings_id}, Amount: {self.amount}, Date: {self.date}>"


class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    user = db.relationship('User', backref='categories', lazy=True)

    def __repr__(self):
        return f"<Category {self.category_id}, Name: {self.category_name}>"


class Expense(db.Model):
    __tablename__ = 'expenses'

    expense_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)

    category = db.relationship('Category', backref='expenses', lazy=True)
    account = db.relationship('Account', backref='expenses', lazy=True)

    def __repr__(self):
        return f"<Expense {self.expense_id}, Amount: {self.amount}, Date: {self.date}>"

class Notification(db.Model):
    __tablename__ = 'notifications'  # match your SQL table name

    notification_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    last_expense_total = db.Column(db.Numeric(10, 2))

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def __repr__(self):
        return f"<Notification {self.notification_id} - User {self.user_id}>"

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='chat_history')
