from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "your_password"
app.config["MYSQL_DB"] = "LobsterNotes"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Create professor account
@app.route("/create-professor-account", methods=["POST"])
def create_professor_account():
    data = request.json

    name = data["name"]
    courses = data["courses"]

    conn = mysql.connection
    cursor = conn.cursor()

    try:
        # Insert User into Professor subclass
        cursor.execute("""
            INSERT INTO User (Name, IsProfessor, Courses)
            VALUES (%s, %s, %s)
        """, (name, True, ", ".join([f"{c.get('Subject','')}{c.get('CatalogNumber','')}" for c in courses])
))
        professor_id = cursor.lastrowid

        #Set badge to True
        cursor.execute("""
            INSERT INTO Professor (UserID, Badge)
            VALUES (%s, %s)
        """, (professor_id, True))

        # Insert all taught courses
        for course in courses:
            cursor.execute("""
                INSERT INTO Course
                (Section, Name, Session, Year, Subject, CatalogNumber, ProfessorID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                course.get("Section"),
                course.get("Name"),
                course["Session"],
                course["Year"],
                course["Subject"],
                course["CatalogNumber"],
                professor_id
            ))
        course_id = cursor.lastrowid
        
        #Add to Teaches relation
        cursor.execute("""
                INSERT INTO Teaches (ProfessorID, CourseID)
                VALUES (%s, %s)
            """, (professor_id, course_id))

        conn.commit()
        return jsonify({"success": True, "ProfessorID": professor_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        cursor.close()
