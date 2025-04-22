from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from db import db, User, Account, Saving, Category, Expense
from forms import LoginForm  # If LoginForm is in forms.py
from decimal import Decimal

# from flask_wtf import FlaskForm
# from wtforms.validators import DataRequired, Length, Email, EqualTo
# from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField, DateField, TextAreaField, IntegerField


# from forms import LoginForm

# from decimal import Decimal
from datetime import datetime

app = Flask(__name__)

import secrets
app.secret_key = secrets.token_hex(16)  # This generates a 32-character hex string

# Database configuration
app.config['SECRET_KEY'] = app.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://norm:Xg7%21dPz%403vLq%249Rt@100.15.171.64/wealthwatcher'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://cazubike:Password#12@localhost/wealth_local'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'cazubike'
# app.config['MYSQL_PASSWORD'] = 'your_password'
# app.config['MYSQL_DB'] = 'wealth_local'

db.init_app(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    print(f"Loading user with ID: {user_id}")
    return User.query.get(int(user_id))

# def load_user(email):
#     return User.query.filter_by(email=email).first()

# TODO: Replace this route with the actual login page once implemented
# '''
# @app.route("/")
# def login():
#     return render_template("login.html")
# '''
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print("User get_id():", user)  
        print("User Password:", user.password)  
        if user.email and check_password_hash(user.password, form.password.data):
            login_user(user)
            print("User logged in:", current_user.is_authenticated)
            print("Redirecting to home")
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.','danger')
    return render_template('login.html', form=form)

# @app.route("/")
@app.route("/home")
@login_required
def home():

    #if "user_id" not in session:
    #        return redirect(url_for("login"))

    # TODO: Replace hardcoded user_id with session["user_id"] once login is implemented

    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    user_id = current_user.user_id

    # Sum of all asset accounts for this user
    total_assets = db.session.query(db.func.sum(Account.balance)) \
        .filter(Account.account_type == 'Asset', Account.user_id == user_id).scalar() or 0

    # Sum of all liability accounts for this user
    total_liabilities = db.session.query(db.func.sum(Account.balance)) \
        .filter(Account.account_type == 'Liability', Account.user_id == user_id).scalar() or 0

    # Calculate net worth
    net_worth = total_assets - total_liabilities

    # Format values with commas and two decimal places
    formatted_net_worth = "{:,.2f}".format(net_worth)
    formatted_assets = "{:,.2f}".format(total_assets)
    formatted_liabilities = "{:,.2f}".format(total_liabilities)

    return render_template("home.html", net_worth=formatted_net_worth,
                           total_assets=formatted_assets,
                           total_liabilities=formatted_liabilities)

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("Inside /register route")
    form = RegisterForm()  # Registration form for new users
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            #firstname=form.firstname.data,
            #lastname=form.lastname.data,
            email=form.email.data,
            password=hashed_password,
            role='User',
            create_time=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)
    # Handle registration logic (e.g., save to database)
    #return redirect(url_for('login'))  # Redirect to login page after successful registration
    # return render_template('register.html', form=form)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    firstname = StringField('First Name', validators=[Length(min=2, max=20)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/expense/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    return "<h3>Add Expense (Coming Soon)</h3>"

# Route to add savings
@app.route('/savings_add', methods=['GET', 'POST'])
@login_required
def savings_add():
    # TODO: Replace hardcoded user_id with session["user_id"] once login is implemented
    #user_id = 1
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    user_id = current_user.user_id
    # Get categories and accounts associated with the current user
    categories = Category.query.filter_by(user_id=user_id).all()
    accounts = Account.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':

        amount = Decimal(request.form['amount']) 
        category_id = request.form['category_id']
        description = request.form['description']
        date = request.form['date']
        account_id = request.form['account_id']

        new_savings = Saving(
            amount=amount,
            description=description,
            date=date,
            category_id=category_id,
            account_id=account_id
        )

        selected_account = Account.query.filter_by(account_id=account_id).first()

        if selected_account:

            if selected_account.account_type == 'Asset':

                selected_account.balance += amount
            elif selected_account.account_type == 'Liability':

                selected_account.balance -= amount

            db.session.commit()

        db.session.add(new_savings)
        db.session.commit()

        return redirect(url_for('home'))

    # Load the form page with account and category dropdowns
    return render_template('savings_add.html', accounts=accounts, categories=categories)

@app.route('/savings_edit/<int:savings_id>', methods=['GET', 'POST'])
@login_required
def savings_edit(savings_id):
    #user_id = 1  # Replace with session["user_id"] once login is implemented
    
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    user_id = current_user.user_id

    saving = Saving.query.get_or_404(savings_id)
    categories = Category.query.filter_by(user_id=user_id).all()
    accounts = Account.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':
        # Get form data
        amount = request.form['amount']
        category_id = request.form['category_id']
        description = request.form['description']
        date = request.form['date']
        account_id = request.form['account_id']

        # Create a new saving record
        new_savings = Saving(
            amount=amount,
            description=description,
            date=date,
            category_id=category_id,
            account_id=account_id
        )

        # Save the record to the database
        db.session.add(new_savings)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('savings_edit.html', saving=saving, categories=categories, accounts=accounts)


@app.route("/savings")
def savings_view():
    user_id = 1  # Replace with session later
    savings = Saving.query.all()
    return render_template("savings_page.html", savings=savings)

@app.route("/account/add", methods=["POST"])
@login_required
def add_account():
    bank_name = request.form['bank_name']
    account_type = request.form['account_type']
    balance = float(request.form['balance'])
    description = request.form.get('description', '')

    new_account = Account(
        bank_name=bank_name,
        account_type=account_type,
        balance=balance,
        description=description,
        user_id=current_user.user_id
    )

    db.session.add(new_account)
    db.session.commit()
    return redirect(url_for('account_manage'))


@app.route('/accounts', methods=['GET'])
@login_required
def account_manage():
    user_id = current_user.user_id
    accounts = Account.query.filter_by(user_id=user_id).all()
    return render_template("accounts_page.html", accounts=accounts)

@app.route('/account/delete/<int:account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for('account_manage'))
    db.session.delete(account)
    db.session.commit()
    return redirect(url_for('account_manage'))

# @app.route("/savings")
# def savings_view():
#     user_id = 1  # Replace with session later
#     savings = Saving.query.all()
#     return render_template("savings_page.html", savings=savings)

# @app.route('/savings/add', methods=['GET', 'POST'])
# @login_required
# def savings_add():
#     return "<h3>Add Savings (Coming Soon)</h3>"

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
