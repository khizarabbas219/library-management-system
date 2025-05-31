from flask import Flask, request, jsonify
from datetime import datetime
from datetime import datetime
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  
app.config['MYSQL_DB'] = 'library_management'

mysql = MySQL(app)

# GET all books
@app.route('/books', methods=['GET'])
def get_books():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()

    books = [
        {'id': row[0], 'title': row[1], 'author': row[2], 'available_copies': row[3]}
        for row in rows
    ]

    cursor.close()
    return jsonify(books)



from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'library_management'

mysql = MySQL(app)

# GET all books
@app.route('/books', methods=['GET'])
def get_books():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    cursor.close()

    books = [
        {'id': row[0], 'title': row[1], 'author': row[2], 'available_copies': row[3]}
        for row in rows
    ]
    return jsonify(books)

# POST a new book
@app.route('/books', methods=['POST'])
def add_books1():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    available_copies = data.get('available_copies')

    if not title or not author or available_copies is None:
        return jsonify({'error': 'Missing fields'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO books (title, author, available_copies) VALUES (%s, %s, %s)",
        (title, author, available_copies)
    )
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Book added successfully'}), 201

# put /Update a Book

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    available_copies = data.get('available_copies')

    if not title or not author or available_copies is None:
        return jsonify({'error': 'Missing fields'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE books SET title=%s, author=%s, available_copies=%s WHERE id=%s",
        (title, author, available_copies, book_id)
    )
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Book updated successfully'})


# delete a book//
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Book deleted successfully'})

# Members management/////// get///
# GET all members
@app.route('/members', methods=['GET'])
def get_members():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM members")
    rows = cursor.fetchall()
    cursor.close()

    members = [
        {'id': row[0], 'name': row[1], 'email': row[2], 'membership_date': row[3].isoformat()}
        for row in rows
    ]
    return jsonify(members)



# POST a new member

from flask import Flask, request, jsonify
from datetime import datetime

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    membership_date = data.get('membership_date')  

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO members (name, email, membership_date) VALUES (%s, %s, %s)",
        (name, email, membership_date or datetime.now().date())
    )
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Member added successfully'}), 201


@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    membership_date = data.get('membership_date')

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    cursor = mysql.connection.cursor()

    # Check if member exists
    cursor.execute("SELECT * FROM members WHERE id = %s", (member_id,))
    existing = cursor.fetchone()
    if not existing:
        cursor.close()
        return jsonify({'error': 'Member not found'}), 404

    # Update member
    cursor.execute("""
        UPDATE members
        SET name = %s, email = %s, membership_date = %s
        WHERE id = %s
    """, (name, email, membership_date or datetime.now().date(), member_id))

    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Member updated successfully'}), 200


# delete members id////////

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM members WHERE id = %s", (member_id,))
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({'message': 'Member deleted'}), 200

#  Issue a Book (POST)////////

@app.route('/issued_books', methods=['POST'])
def issue_book():
    data = request.get_json()
    member_id = data['member_id']
    book_id = data['book_id']

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO issued_books (member_id, book_id, issue_date)
        VALUES (%s, %s, CURDATE())
    """, (member_id, book_id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Book issued successfully'}), 201

#  GET all issued books///////
@app.route('/issued_books', methods=['GET'])
def get_issued_books():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM issued_books")
    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({
            'id': row[0],
            'member_id': row[1],
            'book_id': row[2],
            'issue_date': str(row[3]),
            'return_date': str(row[4]) if row[4] else None
        })
    cursor.close()
    return jsonify(data)

#  PUT – Return a book//////
@app.route('/issued_books/return/<int:id>', methods=['PUT'])
def return_book(id):
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE issued_books SET return_date = CURDATE() WHERE id = %s",
        (id,)
    )
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Book returned successfully'})
# DELETE issued record//////
@app.route('/issued_books/<int:id>', methods=['DELETE'])
def delete_issued_book(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM issued_books WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Issued record deleted'})

# Add Fine////post//
@app.route('/fines', methods=['POST'])
def add_fine():
    data = request.get_json()
    member_id = data.get('member_id')
    book_id = data.get('book_id')
    amount = data.get('amount')

    if not member_id or not book_id or amount is None:
        return jsonify({'error': 'Missing fields'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO fines (member_id, book_id, amount) VALUES (%s, %s, %s)",
        (member_id, book_id, amount)
    )
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Fine added successfully'}), 201

# get fine//////
@app.route('/fines', methods=['GET'])
def get_fines():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM fines")
    fines = cursor.fetchall()
    cursor.close()

    result = []
    for fine in fines:
        result.append({
            'id': fine[0],
            'member_id': fine[1],
            'book_id': fine[2],
            'amount': float(fine[3])
        })

    return jsonify(result), 200
# put fine//////// update/////
@app.route('/fines/<int:fine_id>', methods=['PUT'])
def update_fine(fine_id):
    data = request.get_json()
    amount = data.get('amount')

    if amount is None:
        return jsonify({'error': 'Amount is required'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE fines SET amount = %s WHERE id = %s",
        (amount, fine_id)
    )
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Fine updated successfully'}), 200

# delete fines//////(delete)

@app.route('/fines/<int:fine_id>', methods=['DELETE'])
def delete_fine(fine_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM fines WHERE id = %s", (fine_id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Fine deleted successfully'}), 200

# # Admin Login////////
@app.route('/admin/login', methods=['POST'])
def login_admin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT password FROM admins WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()

    if result and check_password_hash(result[0], password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid '}), 401



if __name__ == '__main__':
    app.run(debug=True)














