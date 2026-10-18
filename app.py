import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/')
def home():
     return render_template('index.html')


@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00248",
        "name": "Seth Claire Palec",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })

# NEW ROUTE: Get all students from the database
@app.route('/students')
def get_students():
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students'
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])

@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


@app.route('/course')
def get_course():
    return jsonify({
        "course": "IT3120",
        "instructor": "Mr. Rene Arduo",
        "schedule": "Every Sunday"
    })

@app.route('/instructor')
def get_instructor():
    instructor = request.args.get('instructor', 'Dr.Arduo')

    return jsonify({
        "message": f"Your instructor in  IT310 subject is {instructor}."
    })



@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')

    return jsonify({
        "message": f"Hello, {name}!"
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
