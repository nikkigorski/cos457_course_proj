from flask import Flask, jsonify, request
from flask_cors import CORS

from flask_mysqldb import MySQL 
import MySQLdb.cursors

app = Flask(__name__)
CORS(app, origins='*') 

#Config for DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'admin' 
app.config['MYSQL_DB'] = 'lobsternotes'

# Initialize MySQL connection. Using PyMySQL as the driver.
mysql = MySQL(app)


#Get professor courses from ProfessorDashboard
@app.route('/api/professor/<int:prof_id>/courses', methods=['GET'])
def get_professor_courses(prof_id):
    cursor = None
    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor) 
        
        search_term = request.args.get('search')
        
        query = """
        SELECT CourseID, Subject, CatalogNumber, Name, Section, Year, ProfessorID
        FROM Course
        WHERE ProfessorID = %s
        """
        params = [prof_id]

        if search_term:
            query += " AND (Name LIKE %s OR Subject LIKE %s)"
            search_param = '%' + search_term + '%'
            params.extend([search_param, search_param])

        cursor.execute(query, tuple(params))
        courses = cursor.fetchall()
        return jsonify(courses)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to fetch courses"}), 500
    finally:
        if cursor: cursor.close()

#Get single course detail 
@app.route('/api/course/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    cursor = None
    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch course info and the prof name
        query = """
        SELECT c.*, u.Name as ProfessorName 
        FROM Course c
        LEFT JOIN User u ON c.ProfessorID = u.UserID
        WHERE c.CourseID = %s
        """
        cursor.execute(query, (course_id,))
        course = cursor.fetchone() # Fetch just one result
        
        if not course:
            return jsonify({"error": "Course not found"}), 404
            
        return jsonify(course)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to fetch details"}), 500
    finally:
        if cursor: cursor.close()


#Get Course Roster
@app.route('/api/course/<int:course_id>/roster', methods=['GET'])
def get_course_roster(course_id):
    cursor = None
    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # QueryUses the View_StudentEnrollments DB View
        query = """
        SELECT 
            UserID,
            StudentName AS Name,     
            MajorOrSubject AS Courses 
        FROM View_StudentEnrollments
        WHERE CourseID = %s;
        """
        
        cursor.execute(query, (course_id,))
        students = cursor.fetchall()
        
        #Return list of students as JSON
        return jsonify(students)
        
    except Exception as e:
        print(f"Database Query Error in get_course_roster: {e}")
        return jsonify({"error": "Failed to fetch student roster from database"}), 500

    finally:
        if cursor:
            cursor.close()


#Runs app
if __name__ == "__main__":
    app.run(debug=True, port=8080)