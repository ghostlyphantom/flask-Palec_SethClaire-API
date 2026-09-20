from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def home():
    return "Welcome to my first API!"


@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00248",
        "name": "Seth Claire Palec",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })

@app.route('/course')
def get_course():
    return jsonify({
        "course": "IT3120",
        "instructor": "Mr. Rene Arduo",
        "schedule": "Every Sunday"
    })

@app.route('/instructor')
def get_instructor():
    subject = request.args.get('instructor', 'Dr.Arduo')

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
    app.run(debug=True)
