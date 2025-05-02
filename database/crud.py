from flask import Flask, request, jsonify
import pymysql
from datetime import datetime

app = Flask(__name__)

# Database connection config
db = pymysql.connect(
    host='localhost',
    user='your_user',
    password='your_password',
    database='wealthwatcher',
    cursorclass=pymysql.cursors.DictCursor
)

# ---- USERS CRUD ----

@app.route('/users', methods=['GET'])
def get_users():
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        return jsonify(cursor.fetchall())

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    with db.cursor() as cursor:
        sql = "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)"
        cursor.execute(sql, (data['email'], data['password'], data.get('role', 'User')))
        db.commit()
        return jsonify({'message': 'User added successfully'}), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    with db.cursor() as cursor:
        sql = "UPDATE users SET email=%s, password=%s, role=%s WHERE user_id=%s"
        cursor.execute(sql, (data['email'], data['password'], data['role'], user_id))
        db.commit()
        return jsonify({'message': 'User updated successfully'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        db.commit()
        return jsonify({'message': 'User deleted successfully'})


# ---- EXPENSES CRUD ----

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    with db.cursor() as cursor:
        sql = """INSERT INTO expenses (amount, description, category_id, account_id)
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (data['amount'], data['description'], data['category_id'], data['account_id']))
        db.commit()
        return jsonify({'message': 'Expense added'}), 201

@app.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    data = request.json
    with db.cursor() as cursor:
        sql = """UPDATE expenses SET amount=%s, description=%s, category_id=%s, account_id=%s
                 WHERE expense_id=%s"""
        cursor.execute(sql, (data['amount'], data['description'], data['category_id'], data['account_id'], expense_id))
        db.commit()
        return jsonify({'message': 'Expense updated'})

@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_id=%s", (expense_id,))
        db.commit()
        return jsonify({'message': 'Expense deleted'})


# ---- SAVINGS CRUD ----

@app.route('/savings', methods=['POST'])
def add_savings():
    data = request.json
    with db.cursor() as cursor:
        sql = """INSERT INTO savings (amount, description, category_id, account_id)
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (data['amount'], data['description'], data['category_id'], data['account_id']))
        db.commit()
        return jsonify({'message': 'Savings added'}), 201

@app.route('/savings/<int:savings_id>', methods=['PUT'])
def update_savings(savings_id):
    data = request.json
    with db.cursor() as cursor:
        sql = """UPDATE savings SET amount=%s, description=%s, category_id=%s, account_id=%s
                 WHERE savings_id=%s"""
        cursor.execute(sql, (data['amount'], data['description'], data['category_id'], data['account_id'], savings_id))
        db.commit()
        return jsonify({'message': 'Savings updated'})

@app.route('/savings/<int:savings_id>', methods=['DELETE'])
def delete_savings(savings_id):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM savings WHERE savings_id=%s", (savings_id,))
        db.commit()
        return jsonify({'message': 'Savings deleted'})


# ---- CATEGORIES CRUD ----

@app.route('/categories', methods=['POST'])
def add_category():
    data = request.json
    with db.cursor() as cursor:
        sql = "INSERT INTO categories (category_name, description, user_id) VALUES (%s, %s, %s)"
        cursor.execute(sql, (data['category_name'], data['description'], data['user_id']))
        db.commit()
        return jsonify({'message': 'Category added'}), 201

@app.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.json
    with db.cursor() as cursor:
        sql = "UPDATE categories SET category_name=%s, description=%s WHERE category_id=%s"
        cursor.execute(sql, (data['category_name'], data['description'], category_id))
        db.commit()
        return jsonify({'message': 'Category updated'})

@app.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM categories WHERE category_id=%s", (category_id,))
        db.commit()
        return jsonify({'message': 'Category deleted'})


# ---- ACCOUNTS CRUD ----

@app.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    data = request.json
    with db.cursor() as cursor:
        sql = """UPDATE accounts SET bank_name=%s, account_type=%s, balance=%s, description=%s
                 WHERE account_id=%s"""
        cursor.execute(sql, (data['bank_name'], data['account_type'], data['balance'], data['description'], account_id))
        db.commit()
        return jsonify({'message': 'Account updated'})

@app.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM accounts WHERE account_id=%s", (account_id,))
        db.commit()
        return jsonify({'message': 'Account deleted'})


if __name__ == '__main__':
    app.run(debug=True)
