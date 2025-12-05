from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "your_password_here"
app.config["MYSQL_DB"] = "LobsterNotes"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route("/create-student-account", methods=["POST"])
def create_student_account():

    data = request.json

    if "name" not in data or "courses" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    name = data["name"]
    courses = data["courses"]

    conn = mysql.connection
    cursor = conn.cursor()

    try:
        # Create User with IsProfessor set to False
        cursor.execute("""
            INSERT INTO User (Name, IsProfessor, Courses)
            VALUES (%s, %s, %s)
        """, (name, False, ", ".join([f"{c.get('Subject','')}{c.get('CatalogNumber','')}" for c in courses])
        ))
        student_id = cursor.lastrowid

        # Create Student
        cursor.execute("""
            INSERT INTO Student (UserID, Name)
            VALUES (%s, %s)
        """, (student_id, name))

        # Verify and enroll in courses
        for course in courses:
            cursor.execute("""
                SELECT CourseID FROM Course
                WHERE Subject = %s
                  AND CatalogNumber = %s
                  AND Section = %s
                  AND Name = %s
                  AND Session = %s
                  AND Year = %s
            """, (
                course["Subject"],
                course["CatalogNumber"],
                course["Section"],
                course["Name"],
                course["Session"],
                course["Year"]
            ))

            row = cursor.fetchone()

            # Course not found
            if not row:
                raise Exception(
                    f"Course not found: "
                    f"{course['Subject']}{course['CatalogNumber']} "
                    f"Section {course['Section']} "
                    f"{course['Session']} {course['Year']}"
                )

            course_id = row["CourseID"]

            # Enroll in course
            cursor.execute("""
                INSERT INTO Enrolled (StudentID, CourseID)
                VALUES (%s, %s)
            """, (student_id, course_id))

        conn.commit()

        return jsonify({
            "success": True,
            "UserID": student_id,
            "IsProfessor": False,
            "CoursesEnrolled": len(courses)
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    finally:
        cursor.close()
