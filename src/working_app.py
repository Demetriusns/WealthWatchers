from flask import Flask, render_template, session, redirect, url_for, request
from db import db, User, Account, Saving, Category, Expense
from decimal import Decimal

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://norm:Xg7%21dPz%403vLq%249Rt@100.15.171.64/wealthwatcher'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# TODO: Replace this route with the actual login page once implemented
'''
@app.route("/")
def login():
    return render_template("login.html")
'''

# Temporary homepage route for testing dashboard functionality

@app.route("/")
#@app.route("/home")
def home():

    #if "user_id" not in session:
    #        return redirect(url_for("login"))

    # TODO: Replace hardcoded user_id with session["user_id"] once login is implemented
    user_id = 1

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


# Route to add savings
@app.route('/savings_add', methods=['GET', 'POST'])
def savings_add():
    # TODO: Replace hardcoded user_id with session["user_id"] once login is implemented
    user_id = 1

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
def savings_edit(savings_id):
    user_id = 1  # Replace with session["user_id"] once login is implemented

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

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
