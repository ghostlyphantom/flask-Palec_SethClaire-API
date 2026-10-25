
import sqlite3
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

DATABASE = 'students.db'

# Database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Validate student information
def validate_student(data):
    if not isinstance(data, dict):
        return None, "Invalid student data"

    required = ['student_id', 'name', 'program', 'year', 'section']

    if any(data.get(field) in (None, '') for field in required):
        return None, "Please provide all required student fields."

    try:
        year = int(data['year'])
    except (ValueError, TypeError):
        return None, "Year must be a number."

    student = {
        'student_id': str(data['student_id']).strip(),
        'name': str(data['name']).strip(),
        'program': str(data['program']).strip(),
        'year': year,
        'section': str(data['section']).strip()
    }

    if not all(student.values()):
        return None, "Student fields cannot be empty."

    return student, None


# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')


# SAMPLE STUDENT API
@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00248",
        "name": "Seth Claire Palec",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# GET ALL DATABASE STUDENTS
@app.route('/students')
def get_students():
    conn = get_db_connection()
    try:
        students = conn.execute(
            'SELECT * FROM students'
        ).fetchall()
        return jsonify([dict(student) for student in students])
    finally:
        conn.close()


# GET STUDENT BY DATABASE ID
@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()
    try:
        student = conn.execute(
            'SELECT * FROM students WHERE id = ?', (id,)
        ).fetchone()

        if student is None:
            return jsonify({"error": "Student not found"}), 404

        return jsonify(dict(student))
    finally:
        conn.close()


# GET STUDENTS BY SECTION
@app.route('/students/section/<section>')
def get_students_by_section(section):
    conn = get_db_connection()
    try:
        students = conn.execute(
            'SELECT * FROM students WHERE section = ?', (section,)
        ).fetchall()
        return jsonify([dict(student) for student in students])
    finally:
        conn.close()


# GET ALL STUDENTS THROUGH API
@app.route('/api/students', methods=['GET'])
def api_get_students():
    return get_students()


# ADD A LOCAL STUDENT
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json(silent=True)
    student, error = validate_student(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                student['student_id'],
                student['name'],
                student['program'],
                student['year'],
                student['section'],
                'Local'
            )
        )
        conn.commit()

        return jsonify({
            "message": "Student added successfully.",
            "id": cursor.lastrowid
        }), 201

    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({
            "error": "Unable to add student. Check whether the Student ID already exists."
        }), 409
    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Unable to add student")
        return jsonify({"error": "Database error while adding student."}), 500
    finally:
        conn.close()


# GET STUDENT THROUGH API
@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    return get_student_by_id(id)


# UPDATE A STUDENT
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True)
    student, error = validate_student(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    try:
        existing = conn.execute(
            'SELECT source FROM students WHERE id = ?', (id,)
        ).fetchone()

        if existing is None:
            return jsonify({"error": "Student not found"}), 404

        source = data.get('source', existing['source'])

        conn.execute(
            """UPDATE students SET
            student_id = ?, name = ?, program = ?,
            year = ?, section = ?, source = ?
            WHERE id = ?""",
            (
                student['student_id'],
                student['name'],
                student['program'],
                student['year'],
                student['section'],
                source,
                id
            )
        )
        conn.commit()

        return jsonify({"message": "Student updated successfully."})

    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({"error": "This Student ID may already exist."}), 409
    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Unable to update student")
        return jsonify({"error": "Database error while updating student."}), 500
    finally:
        conn.close()


# DELETE A STUDENT
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            'DELETE FROM students WHERE id = ?', (id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student deleted successfully."})
    finally:
        conn.close()


# CLASSMATE'S EXTERNAL API
CLASSMATE_API = "https://jezalyn-indic.onrender.com/api/students"


def fetch_classmate_records():
    try:
        response = requests.get(CLASSMATE_API, timeout=15)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            return jsonify({
                "error": "Classmate API did not return a list of records."
            }), 502

        return jsonify(data)

    except requests.RequestException:
        app.logger.exception("Classmate API request failed")
        return jsonify({
            "error": "Unable to retrieve classmate records. Check the API URL."
        }), 502
    except ValueError:
        return jsonify({
            "error": "Classmate API returned invalid JSON."
        }), 502


@app.route('/api/classmate-students', methods=['GET'])
def get_classmate_students():
    return fetch_classmate_records()


@app.route('/classmate-records', methods=['GET'])
def partner_records():
    return fetch_classmate_records()


# IMPORT / SAVE A CLASSMATE'S RECORD
def save_classmate_record():
    data = request.get_json(silent=True)
    student, error = validate_student(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    try:
        existing = conn.execute(
            'SELECT id FROM students WHERE student_id = ?',
            (student['student_id'],)
        ).fetchone()

        if existing:
            return jsonify({
                "message": "This student ID already exists in your database."
            }), 409

        cursor = conn.execute(
            """INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                student['student_id'],
                student['name'],
                student['program'],
                student['year'],
                student['section'],
                'Classmate API'
            )
        )
        conn.commit()

        return jsonify({
            "message": "Classmate record saved successfully.",
            "id": cursor.lastrowid,
            "source": "Classmate API"
        }), 201

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Unable to import classmate record")
        return jsonify({
            "error": "Database error while saving record."
        }), 500
    finally:
        conn.close()


@app.route('/import-student', methods=['POST'])
def import_student():
    return save_classmate_record()


@app.route('/api/import-classmate-student', methods=['POST'])
def import_partner_student():
    return save_classmate_record()


# COURSE API
@app.route('/course')
def get_course():
    return jsonify({
        "course": "IT3120",
        "instructor": "Dr. Rene Arduo",
        "schedule": "Every Sunday"
    })


# INSTRUCTOR API
@app.route('/instructor')
def get_instructor():
    instructor = request.args.get('instructor', 'Dr. Arduo')
    return jsonify({
        "message": f"Your instructor in IT310 subject is {instructor}."
    })


# GREETING API
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({"message": f"Hello, {name}!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
