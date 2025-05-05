import uuid
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from wtforms import StringField, PasswordField,SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from db import db, User, Account, Saving, Category, Expense, Notification
from forms import LoginForm  # If LoginForm is in forms.py
from forms import RegisterForm
from decimal import Decimal
from functools import wraps
#from datetime import datetime
from sqlalchemy import func, extract, and_


# from flask_wtf import FlaskForm
# from wtforms.validators import DataRequired, Length, Email, EqualTo
# from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField, DateField, TextAreaField, IntegerField


# from forms import LoginForm

# from decimal import Decimal
from datetime import datetime

app = Flask(__name__)

import secrets
app.secret_key = secrets.token_hex(16)  # This generates a 32-character hex string
scheduler = BackgroundScheduler()

# Database configuration
app.config['SECRET_KEY'] = app.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://norm:Xg7%21dPz%403vLq%249Rt@100.15.171.64/wealthwatcher'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#smremhvxxdwkgoad

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cazubike@yahoo.com'
app.config['MAIL_PASSWORD'] = 'smremhvxxdwkgoad'
app.config['MAIL_DEFAULT_SENDER'] = 'cazubike@yahoo.com'
mail = Mail(app)




# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://cazubike:Password#12@localhost/wealth_local'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'cazubike'
# app.config['MYSQL_PASSWORD'] = 'your_password'
# app.config['MYSQL_DB'] = 'wealth_local'

from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    question = data.get("message")

    try:
        # Call OpenAI API
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": question}]
        )
        answer = response.choices[0].message.content.strip()


        # Save to DB
        chat_entry = ChatHistory(user_id=current_user.user_id, question=question, response=answer)
        db.session.add(chat_entry)
        db.session.commit()

        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Helper function for the notification system.
def check_and_create_expense_alert(user_id):
    account_ids = [acc.account_id for acc in Account.query.filter_by(user_id=user_id).all()]

    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year

    total_savings = db.session.query(func.sum(Saving.amount)).filter(
        Saving.account_id.in_(account_ids),
        extract('month', Saving.date) == current_month,
        extract('year', Saving.date) == current_year
    ).scalar() or 0

    total_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.account_id.in_(account_ids),
        extract('month', Expense.date) == current_month,
        extract('year', Expense.date) == current_year
    ).scalar() or 0


    if abs(total_expenses) == 0 and total_savings == 0:
        return

    existing_alert = Notification.query.filter_by(user_id=user_id, title="Expense Alert").filter(
        extract('month', Notification.timestamp) == current_month,
        extract('year', Notification.timestamp) == current_year
    ).first()

    if existing_alert:
        previous_total = existing_alert.last_expense_total or 0
        if abs(total_expenses) > previous_total:
            existing_alert.message = (
                f"Alert: Your total expenses this month (${abs(total_expenses):,.2f}) "
                f"have exceeded your savings (${total_savings:,.2f}). Please review your spending."
            )
            existing_alert.timestamp = datetime.utcnow()
            existing_alert.last_expense_total = abs(total_expenses)
            existing_alert.is_read = False
            db.session.commit()
    else:
        if abs(total_expenses) > total_savings:
            notification = Notification(
                user_id=user_id,
                title="Expense Alert",
                message=(
                    f"Alert: Your total expenses this month (${abs(total_expenses):,.2f}) "
                    f"have exceeded your savings (${total_savings:,.2f}). Please review your spending."
                ),
                timestamp=datetime.utcnow(),
                last_expense_total=abs(total_expenses),
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()

def get_week_range(reference_date=None):
    if reference_date is None:
        reference_date = datetime.utcnow()

    weekday = reference_date.isoweekday() % 7
    start_of_week = reference_date - timedelta(days=weekday)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    return start_of_week, end_of_week

# Helper function for weekely notification
def send_weekly_summary():
    start_of_week, end_of_week = get_week_range()

    users = User.query.all()

    for user in users:
        accounts = Account.query.filter_by(user_id=user.user_id).all()
        account_ids = [account.account_id for account in accounts]

        savings = Saving.query.filter(
            and_(
                Saving.account_id.in_(account_ids),
                Saving.date >= start_of_week,
                Saving.date <= end_of_week
            )
        ).all()

        expenses = Expense.query.filter(
            and_(
                Expense.account_id.in_(account_ids),
                Expense.date >= start_of_week,
                Expense.date <= end_of_week
            )
        ).all()

        if not savings and not expenses:
            continue  # Skip users with no activity

        savings_summary = "<br>".join([f"- ${s.amount} on {s.date.strftime('%Y-%m-%d')}" for s in savings])
        expenses_summary = "<br>".join([f"- ${e.amount} on {e.date.strftime('%Y-%m-%d')}" for e in expenses])

        week_range = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"
        message = f"""Here is your weekly summary for <strong>{week_range}</strong>:<br><br>

        💰 <strong>Savings:</strong><br>
        {savings_summary if savings_summary else "No savings this week."}<br><br>

        💸 <strong>Expenses:</strong><br>
        {expenses_summary if expenses_summary else "No expenses this week."}
        """

        notification = Notification(
            user_id=user.user_id,
            title="Weekly Financial Summary",
            message=message,
            is_read=False
        )
        db.session.add(notification)

    db.session.commit()

def schedule_weekly_summary():
    send_weekly_summary()

scheduler.add_job(schedule_weekly_summary, CronTrigger(day_of_week='sun', hour=0, minute=0, second=0))



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
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    user_id = current_user.user_id

    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    # Sum of all asset accounts for this user
    total_assets = db.session.query(db.func.sum(Account.balance)) \
        .filter(Account.account_type == 'Asset', Account.user_id == user_id).scalar() or 0

    # Sum of all liability accounts for this user
    total_liabilities = db.session.query(db.func.sum(Account.balance)) \
        .filter(Account.account_type == 'Liability', Account.user_id == user_id).scalar() or 0

    # Calculate net worth
    net_worth = total_assets + total_liabilities

    # Format values with commas and two decimal places
    formatted_net_worth = "{:,.2f}".format(net_worth)
    formatted_assets = "{:,.2f}".format(total_assets)
    formatted_liabilities = "{:,.2f}".format(total_liabilities)

    return render_template("home.html", net_worth=formatted_net_worth,
                           total_assets=formatted_assets,
                           total_liabilities=formatted_liabilities,
                           unread_count=unread_count)

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

@app.route('/event/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    user_id = current_user.user_id
    categories = Category.query.filter_by(user_id=user_id).all()
    accounts = Account.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':
        amount = Decimal(request.form['amount'])
        category_id = request.form['category_id']
        description = request.form['description']
        date = request.form['date']
        account_id = request.form['account_id']

        selected_account = Account.query.filter_by(account_id=account_id).first()


        if selected_account and selected_account.account_type in ['Asset', 'Liability']:
            if selected_account.account_type == 'Asset':
                selected_account.balance += amount
            elif selected_account.account_type == 'Liability':
                selected_account.balance += amount
            db.session.commit()

        # Save to the appropriate table
        if amount >= 0:
            new_event = Saving(amount=amount, description=description, date=date,
                               category_id=category_id, account_id=account_id)
            db.session.add(new_event)
        else:
            new_event = Expense(amount=amount, description=description, date=date,
                                category_id=category_id, account_id=account_id)
            db.session.add(new_event)

        db.session.commit()
        check_and_create_expense_alert(user_id)
        return redirect(url_for('home'))

    return render_template('event_add.html', accounts=accounts, categories=categories)

@app.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    user_id = current_user.user_id
    event = Saving.query.get_or_404(event_id)
    categories = Category.query.filter_by(user_id=user_id).all()
    accounts = Account.query.filter_by(user_id=user_id).all()
    if request.method == 'POST':
        event.amount = request.form['amount']
        event.category_id = request.form['category_id']
        event.description = request.form['description']
        event.date = request.form['date']
        event.account_id = request.form['account_id']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('event_edit.html', event=event, categories=categories, accounts=accounts)

@app.route("/events")
@login_required
def events_view():
    events = db.session.query(Saving).join(Account).filter(Account.user_id == current_user.user_id).all()
    return render_template("events_page.html", events=events)

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
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return render_template("accounts_page.html", accounts=accounts,  unread_count=unread_count)

@app.route('/account/delete/<int:account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for('account_manage'))


    Saving.query.filter_by(account_id=account_id).delete()


    db.session.delete(account)
    db.session.commit()

    flash("Account and related savings deleted successfully.", "success")
    return redirect(url_for('account_manage'))

@app.route('/account/edit/<int:account_id>', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    account = Account.query.get_or_404(account_id)

    # Make sure this account belongs to the logged-in user
    if account.user_id != current_user.user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for('account_manage'))

    if request.method == 'POST':
        account.bank_name = request.form['bank_name']
        account.account_type = request.form['account_type']
        account.balance = float(request.form['balance'])
        account.description = request.form.get('description', '')
        db.session.commit()
        return redirect(url_for('account_manage'))

    return render_template('account_form.html', account=account)

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def category_manage():

    user_id = current_user.user_id
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    if request.method == 'POST':
        new_category_name = request.form.get('category_name')
        new_description = request.form.get('description')

        if new_category_name:
            new_category = Category(
                category_name=new_category_name,
                description=new_description,
                user_id=current_user.user_id
            )
            db.session.add(new_category)
            db.session.commit()

            # If AJAX request, return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'category': {
                        'category_name': new_category.category_name,
                        'description': new_category.description or "No description",
                        'category_id': new_category.category_id
                    }
                })

            return redirect(url_for('category_manage'))

    user_categories = Category.query.filter_by(user_id=current_user.user_id).all()
    return render_template('categories.html', categories=user_categories,  unread_count=unread_count)

@app.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.filter_by(category_id=category_id, user_id=current_user.user_id).first()
    if category:
        category_name = category.category_name
        db.session.delete(category)
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'category_name': category_name})

    return redirect(url_for('category_manage'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin.html', users=users)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.email}' has been deleted.", "success")
    else:
        flash("User not found.", "warning")
    return redirect(url_for('admin_dashboard'))

@app.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    user_id = current_user.user_id

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.timestamp.desc()).all()
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    return render_template('notification.html', notifications=notifications, unread_count=unread_count)


@app.route('/mark_as_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_as_read(notification_id):
    # Mark the notification as read
    notification = Notification.query.get(notification_id)
    if notification and notification.user_id == current_user.user_id:
        notification.is_read = True
        db.session.commit()

    # Get the count of unread notifications
    unread_count = Notification.query.filter_by(user_id=current_user.user_id, is_read=False).count()

    return jsonify({'unread_count': unread_count})


@app.route("/delete_notification/<int:notification_id>", methods=["DELETE"])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.filter_by(notification_id=notification_id, user_id=current_user.user_id).first()
    if notification:
        is_unread = not notification.is_read
        db.session.delete(notification)
        db.session.commit()

        # Get updated unread count
        unread_count = Notification.query.filter_by(user_id=current_user.user_id, is_read=False).count()

        return jsonify({"success": True, "unread_count": unread_count})
    else:
        return jsonify({"success": False, "error": "Notification not found"}), 404
# This is for testing purposes. Use the link http://100.15.171.64:5000/test_weekly_summary and refresh notification page.
# This should genearate a message.
@app.route("/test_weekly_summary")
def test_weekly_summary():
    send_weekly_summary()
    return "Weekly summary notifications generated successfully!"

# @app.route('/admin')
# @login_required
# @admin_required
# def admin_dashboard():
#     users = User.query.all()
#     return render_template('admin.html', users=users)

# @app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
# @login_required
# @admin_required
# def delete_user(user_id):
#     user = User.query.get(user_id)
#     if user:
#         db.session.delete(user)
#         db.session.commit()
#         flash(f"User '{user.email}' has been deleted.", "success")
#     else:
#         flash("User not found.", "warning")
#     return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)

    if user.email == current_user.email:
        flash("You cannot change your own admin status.", "warning")
        return redirect(url_for('admin_dashboard'))

    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"Admin status updated for {user.email}", "success")
    return redirect(url_for('admin_dashboard'))

# --- Forgot Password ---
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            reset_token = str(uuid.uuid4())  # Generate a unique token for password reset
            #db.execute("Update users set reset_token = ? where email = ?", (reset_token, email))
            #db.session.commit()
            user.reset_token = reset_token
            db.session.commit()
            reset_link = url_for('reset_password', token=reset_token, _external=True)
            print(f"Reset link: {reset_link}")  # For debugging purposes

            #msg = Message(subject, recipients=[to], sender=cfg.get('SMTP', 'sender'))

            #send mail with reset link
            # msg = Message("Test from Flask",
            #       recipients=["recipient@example.com"],
            #       body="This is a test email sent using Yahoo SMTP.")


            msg = Message("Password Reset Request", recipients=[email])
            msg.body = f"To reset your password, click the following link: {reset_link}\nIf you did not request this, please ignore this email."
            #msg.body = f"To reset your password, click the following link: {reset_link}\nIf you did not request this, please ignore this email."
            mail.send(msg)
            flash("A password reset link has been sent to your email address.", "info")
            return redirect(url_for('login'))

            # Here you would send an email with a reset link
            flash('A password reset link has been sent to your email.', 'success')
        else:
            flash('Email not found.', 'danger')
    return render_template('forgot_password.html')


# --- Reset Password ---
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form['password']
        user = User.query.filter_by(reset_token=token).first()

        if user:
            user.password = generate_password_hash(new_password)
            user.reset_token = None  # Clear the reset token after successful reset
            db.session.add(user)
            db.session.commit()
            flash('Your password has been reset successfully! You can now log in.')
            return redirect(url_for('login'))
        else:
            flash('Invalid or expired token.')
            #return redirect(url_for('forgot_password'))
            return render_template('reset_password.html', token=None)
    return render_template('reset_password.html', token=token)


if __name__ == "__main__":
    scheduler.start()
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
