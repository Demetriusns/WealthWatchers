from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError

# from flask import Flask, render_template, redirect, url_for, flash
# from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# from werkzeug.security import check_password_hash
# from db import db, User
# from forms import LoginForm

class LoginForm(FlaskForm):
    email = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', render_kw={"size": 20}, validators=[DataRequired(), Length(min=3)])
    firstname = StringField('Firstname', render_kw={"size": 20}, validators=[DataRequired(), Length(min=3)])
    lastname = StringField('Lastname', render_kw={"size": 20}, validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', render_kw={"size": 20}, validators=[DataRequired()])
    confirmpassword = PasswordField('Confirmpassword', render_kw={"size": 20}, validators=[DataRequired()])
    role = StringField('role', render_kw={"size": 20}, validators=[DataRequired(), Length(min=3)])
    submit = SubmitField('Register')

# class ExpenseForm(FlaskForm):
#     amount = FloatField('Amount', validators=[DataRequired()])
#     category = SelectField('Category', choices=[('Food','Food'), ('Transport','Transport'), ('Bills','Bills')])
#     description = StringField('Description')
#     submit = SubmitField('Add Expense')
