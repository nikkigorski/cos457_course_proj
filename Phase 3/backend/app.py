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
# Try common socket locations - the driver will use the first one that exists
import os
socket_paths = [
    '/tmp/mysql.sock',  # Standard Linux location
    '/var/run/mysqld/mysql.sock',  # Another common Linux location
    '/home/nikki.gorski/mysql.sock'  # Local installation
]
for socket_path in socket_paths:
    if os.path.exists(socket_path):
        app.config['MYSQL_UNIX_SOCKET'] = socket_path
        break

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
        
        # Query students enrolled in the course
        query = """
        SELECT 
            u.UserID,
            u.Name,     
            u.Courses 
        FROM Student s
        JOIN User u ON s.UserID = u.UserID
        JOIN Enrolled e ON s.UserID = e.StudentID
        WHERE e.CourseID = %s;
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

#create a new course
@app.route('/api/courses', methods=['POST'])
def add_course():
    cursor = None
    try:
        #Get data from frontend
        data = request.get_json()
        
        #validate frontend required fields
        subject = data.get('Subject')
        catalog_number = data.get('CatalogNumber')
        name = data.get('Name')
        section = data.get('Section')
        year = data.get('Year')
        session = data.get('Session')
        professor_id = data.get('ProfessorID')

        conn = mysql.connection
        # Use DictCursor to easily access ProfessorID later, though not strictly required for INSERT
        cursor = conn.cursor(MySQLdb.cursors.DictCursor) 
        
        #Insert query
        query = """
        INSERT INTO Course (Subject, CatalogNumber, Name, Section, Year, Session, ProfessorID)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        #Execute query
        cursor.execute(query, (subject, catalog_number, name, section, year, session, professor_id))
        
        #Save insert to DB
        conn.commit()

        return jsonify({"message": "Course created successfully", "course_id": cursor.lastrowid}), 201
    except Exception as e:
        print(f"Error adding course: {e}")
        return jsonify({"error": "Failed to add course"}), 500
    finally:
        if cursor: cursor.close()

#Update course
@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    cursor = None
    try:
        data = request.get_json()
        
        # Attributes that can be updated
        name = data.get('Name')
        section = data.get('Section')
        session = data.get('Session')
        year = data.get('Year')

        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor) 
        
        #Update query
        query = """
        UPDATE Course
        SET Name = %s, Section = %s, Session = %s, Year = %s
        WHERE CourseID = %s
        """
        
        # Execute query
        cursor.execute(query, (name, section, session, year, course_id))
        #save to DB
        conn.commit()

        if cursor.rowcount == 0:
             return jsonify({"error": "Course not found or no changes made"}), 404
             
        return jsonify({"message": "Course updated successfully"}), 200
    except Exception as e:
        print(f"Error updating course: {e}")
        return jsonify({"error": "Failed to update course"}), 500
    finally:
        if cursor: cursor.close()


#Delete Course (ENSURE PROFESSOR ONLY -> Will delete all records attached to course)
@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    cursor = None
    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor) 
        
        # Delete query
        query = """
        DELETE FROM Course
        WHERE CourseID = %s
        """
        
        #Execute query
        cursor.execute(query, (course_id,))
        
        #update DB
        conn.commit()

        if cursor.rowcount == 0:
             return jsonify({"error": "Course not found"}), 404
             
        return jsonify({"message": f"Course {course_id} deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting course: {e}")
        return jsonify({"error": "Failed to delete course"}), 500
    finally:
        if cursor: cursor.close()



#Runs app
if __name__ == "__main__":
    app.run(debug=True, port=8080)