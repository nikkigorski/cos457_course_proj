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
# Try common socket locations 
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


# ==================== RESOURCE/NOTES ENDPOINTS ====================

# Get all resources/notes with optional search and filtering
@app.route('/api/resources', methods=['GET'])
def get_resources():
    cursor = None
    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Get query parameters for filtering
        search_term = request.args.get('search')
        topic = request.args.get('topic')
        format_type = request.args.get('format')
        subject = request.args.get('subject')
        
        # Base query joining all resource types
        query = """
        SELECT 
            r.ResourceID,
            r.Date,
            r.DateFor,
            r.Author,
            r.Topic as Title,
            r.Topic,
            r.Keywords,
            r.Rating,
            r.Format,
            r.isVerified,
            n.Body,
            w.Link as Url,
            v.Duration,
            v.Link as VideoUrl,
            p.Link as PdfUrl,
            i.Link as ImageUrl,
            i.Size as ImageSize
        FROM Resource r
        LEFT JOIN Note n ON r.ResourceID = n.ResourceID
        LEFT JOIN Website w ON r.ResourceID = w.ResourceID
        LEFT JOIN Video v ON r.ResourceID = v.ResourceID
        LEFT JOIN pdf p ON r.ResourceID = p.ResourceID
        LEFT JOIN Image i ON r.ResourceID = i.ResourceID
        WHERE 1=1
        """
        params = []
        
        # Add search filter
        if search_term:
            query += " AND (r.Topic LIKE %s OR r.Keywords LIKE %s OR r.Author LIKE %s)"
            search_param = '%' + search_term + '%'
            params.extend([search_param, search_param, search_param])
        
        # Add topic filter
        if topic:
            query += " AND r.Topic LIKE %s"
            params.append('%' + topic + '%')
        
        # Add format filter
        if format_type:
            query += " AND r.Format = %s"
            params.append(format_type)
        
        # Add subject filter (search in topic/keywords)
        if subject:
            query += " AND (r.Topic LIKE %s OR r.Keywords LIKE %s)"
            subject_param = '%' + subject + '%'
            params.extend([subject_param, subject_param])
        
        query += " ORDER BY r.Date DESC"
        
        cursor.execute(query, tuple(params))
        resources = cursor.fetchall()
        
        # Consolidate URL field based on format
        for resource in resources:
            if resource['Format'] == 'Website' and resource['Url']:
                pass  # Already has Url
            elif resource['Format'] == 'Video':
                resource['Url'] = resource['VideoUrl']
            elif resource['Format'] == 'Pdf':
                resource['Url'] = resource['PdfUrl']
            elif resource['Format'] == 'Image':
                resource['Url'] = resource['ImageUrl']
            
            # Clean up unnecessary fields
            if 'VideoUrl' in resource:
                del resource['VideoUrl']
            if 'PdfUrl' in resource:
                del resource['PdfUrl']
            if 'ImageUrl' in resource:
                del resource['ImageUrl']
        
        return jsonify(resources)
    except Exception as e:
        print(f"Error fetching resources: {e}")
        return jsonify({"error": "Failed to fetch resources"}), 500
    finally:
        if cursor: cursor.close()


# Get single resource/note by ID
@app.route('/api/resources/<int:resource_id>', methods=['GET'])
def get_resource_details(resource_id):
    cursor = None
    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Direct query instead of stored procedure (DictCursor doesn't support stored_results)
        query = """
        SELECT 
            r.ResourceID,
            r.Date,
            r.DateFor,
            r.Author,
            r.Topic as Title,
            r.Topic,
            r.Keywords,
            r.Rating,
            r.Format,
            r.isVerified,
            n.Body,
            w.Link as WebsiteUrl,
            v.Duration,
            v.Link as VideoUrl,
            p.Link as PdfUrl,
            p.Body as PdfBody,
            i.Link as ImageUrl,
            i.Size as ImageSize,
            (SELECT AVG(Score) FROM Rating WHERE ResourceID = r.ResourceID) as Average_Rating
        FROM Resource r
        LEFT JOIN Note n ON r.ResourceID = n.ResourceID
        LEFT JOIN Website w ON r.ResourceID = w.ResourceID
        LEFT JOIN Video v ON r.ResourceID = v.ResourceID
        LEFT JOIN pdf p ON r.ResourceID = p.ResourceID
        LEFT JOIN Image i ON r.ResourceID = i.ResourceID
        WHERE r.ResourceID = %s
        """
        cursor.execute(query, (resource_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Resource not found"}), 404
        
        # Consolidate URL field
        if result.get('Format') == 'Website':
            result['Url'] = result.get('WebsiteUrl') or result.get('Web_Address')
        elif result.get('Format') == 'Video':
            result['Url'] = result.get('VideoUrl')
        elif result.get('Format') == 'Pdf':
            result['Url'] = result.get('PdfUrl')
        elif result.get('Format') == 'Image':
            result['Url'] = result.get('ImageUrl')
        elif result.get('Format') == 'Note':
            result['Body'] = result.get('Body') or result.get('Note_Body')
        
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching resource details: {e}")
        return jsonify({"error": "Failed to fetch resource details"}), 500
    finally:
        if cursor: cursor.close()


# Create a new resource/note
@app.route('/api/resources', methods=['POST'])
def create_resource():
    cursor = None
    try:
        from datetime import datetime
        data = request.get_json()
        
        # Required fields
        author = data.get('Author')
        topic = data.get('Topic')
        format_type = data.get('Format')
        
        # DateFor defaults to today if not provided
        date_for = data.get('DateFor') or datetime.now().strftime('%Y-%m-%d')
        
        # Optional fields
        keywords = data.get('Keywords')
        body = data.get('Body')
        link = data.get('Link') or data.get('Url')
        duration = data.get('Duration')
        size = data.get('Size')
        
        if not all([author, topic, format_type]):
            return jsonify({"error": "Missing required fields: Author, Topic, Format"}), 400
        
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if author exists, if not create them
        cursor.execute("SELECT UserID FROM User WHERE Name = %s", (author,))
        author_exists = cursor.fetchone()
        
        if not author_exists:
            # Create new user for the author
            cursor.execute(
                "INSERT INTO User (Name, Courses, IsProfessor) VALUES (%s, NULL, FALSE)",
                (author,)
            )
            conn.commit()
            
            # Get the new user ID and create Student entry
            cursor.execute("SELECT UserID FROM User WHERE Name = %s", (author,))
            new_user = cursor.fetchone()
            if new_user:
                user_id = new_user['UserID']
                cursor.execute("INSERT INTO Student (UserID) VALUES (%s)", (user_id,))
                conn.commit()
        
        insert_query = """
        INSERT INTO Resource (Date, DateFor, Author, Topic, Keywords, Format)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(insert_query, (today, date_for, author, topic, keywords, format_type))
        conn.commit()
        
        resource_id = cursor.lastrowid
        
        # Now insert format-specific data
        if format_type == 'Note' and body:
            cursor.execute("INSERT INTO Note (ResourceID, Body) VALUES (%s, %s)", (resource_id, body))
        elif format_type == 'Website' and link:
            cursor.execute("INSERT INTO Website (ResourceID, Link) VALUES (%s, %s)", (resource_id, link))
        elif format_type == 'Pdf' and (link or body):
            cursor.execute("INSERT INTO pdf (ResourceID, Body, Link) VALUES (%s, %s, %s)", (resource_id, body, link))
        elif format_type == 'Image' and link:
            cursor.execute("INSERT INTO Image (ResourceID, Size, Link) VALUES (%s, %s, %s)", (resource_id, size, link))
        elif format_type == 'Video' and link:
            cursor.execute("INSERT INTO Video (ResourceID, Duration, Link) VALUES (%s, %s, %s)", (resource_id, duration, link))
        
        conn.commit()
        
        return jsonify({
            "message": "Resource created successfully",
            "resource_id": resource_id
        }), 201
        
    except Exception as e:
        print(f"Error creating resource: {e}")
        return jsonify({"error": f"Failed to create resource: {str(e)}"}), 500
    finally:
        if cursor: cursor.close()


# Submit a rating for a resource
@app.route('/api/resources/<int:resource_id>/ratings', methods=['POST'])
def submit_rating(resource_id):
    cursor = None
    try:
        data = request.get_json()
        
        poster = data.get('Poster')
        score = data.get('Score')
        date = data.get('Date')
        
        if not all([poster, score, date]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Validate score range
        try:
            score_float = float(score)
            if score_float < 0.0 or score_float > 5.0:
                return jsonify({"error": "Score must be between 0.0 and 5.0"}), 400
        except ValueError:
            return jsonify({"error": "Invalid score format"}), 400
        
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if poster exists as a user, if not create them
        cursor.execute("SELECT UserID FROM User WHERE Name = %s", (poster,))
        poster_exists = cursor.fetchone()
        
        if not poster_exists:
            # Create new user for the poster
            cursor.execute(
                "INSERT INTO User (Name, Courses, IsProfessor) VALUES (%s, NULL, FALSE)",
                (poster,)
            )
            conn.commit()
            
            # Get the new user ID and create Student entry
            cursor.execute("SELECT UserID FROM User WHERE Name = %s", (poster,))
            new_user = cursor.fetchone()
            if new_user:
                user_id = new_user['UserID']
                cursor.execute("INSERT INTO Student (UserID) VALUES (%s)", (user_id,))
                conn.commit()
        
        # Use stored procedure SP_Rating_Rate
        cursor.callproc('SP_Rating_Rate', [
            resource_id,
            poster,
            score,
            date
        ])
        
        conn.commit()
        
        # Update the average rating in Resource table
        cursor.execute("""
            UPDATE Resource 
            SET Rating = (
                SELECT ROUND(AVG(Score), 1) 
                FROM Rating 
                WHERE ResourceID = %s
            )
            WHERE ResourceID = %s
        """, (resource_id, resource_id))
        
        conn.commit()
        
        return jsonify({"message": "Rating submitted successfully"}), 201
        
    except Exception as e:
        print(f"Error submitting rating: {e}")
        return jsonify({"error": "Failed to submit rating"}), 500
    finally:
        if cursor: cursor.close()


# Get ratings for a specific resource
@app.route('/api/resources/<int:resource_id>/ratings', methods=['GET'])
def get_resource_ratings(resource_id):
    cursor = None
    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        query = """
        SELECT RatingID, Poster, Score, Date
        FROM Rating
        WHERE ResourceID = %s
        ORDER BY Date DESC
        """
        
        cursor.execute(query, (resource_id,))
        ratings = cursor.fetchall()
        
        return jsonify(ratings)
    except Exception as e:
        print(f"Error fetching ratings: {e}")
        return jsonify({"error": "Failed to fetch ratings"}), 500
    finally:
        if cursor: cursor.close()


# Get resources by subject/course
@app.route('/api/subjects/<subject_code>/resources', methods=['GET'])
def get_resources_by_subject(subject_code):
    cursor = None
    try:
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Get subject name first
        cursor.execute("SELECT Name FROM Subject WHERE Code = %s", (subject_code,))
        subject = cursor.fetchone()
        
        if not subject:
            return jsonify({"error": "Subject not found"}), 404
        
        subject_name = subject['Name']
        
        # Search for resources matching the subject in Topic or Keywords
        query = """
        SELECT 
            r.ResourceID,
            r.Date,
            r.DateFor,
            r.Author,
            r.Topic as Title,
            r.Topic,
            r.Keywords,
            r.Rating,
            r.Format,
            r.isVerified,
            n.Body,
            w.Link as Url,
            v.Link as VideoUrl,
            p.Link as PdfUrl,
            i.Link as ImageUrl
        FROM Resource r
        LEFT JOIN Note n ON r.ResourceID = n.ResourceID
        LEFT JOIN Website w ON r.ResourceID = w.ResourceID
        LEFT JOIN Video v ON r.ResourceID = v.ResourceID
        LEFT JOIN pdf p ON r.ResourceID = p.ResourceID
        LEFT JOIN Image i ON r.ResourceID = i.ResourceID
        WHERE r.Topic LIKE %s OR r.Keywords LIKE %s
        ORDER BY r.Date DESC
        """
        
        search_param = '%' + subject_code + '%'
        cursor.execute(query, (search_param, search_param))
        resources = cursor.fetchall()
        
        # Consolidate URLs
        for resource in resources:
            if resource['Format'] == 'Video':
                resource['Url'] = resource['VideoUrl']
            elif resource['Format'] == 'Pdf':
                resource['Url'] = resource['PdfUrl']
            elif resource['Format'] == 'Image':
                resource['Url'] = resource['ImageUrl']
            
            if 'VideoUrl' in resource:
                del resource['VideoUrl']
            if 'PdfUrl' in resource:
                del resource['PdfUrl']
            if 'ImageUrl' in resource:
                del resource['ImageUrl']
        
        return jsonify({
            "subject": subject_name,
            "code": subject_code,
            "resources": resources
        })
    except Exception as e:
        print(f"Error fetching resources by subject: {e}")
        return jsonify({"error": "Failed to fetch resources"}), 500
    finally:
        if cursor: cursor.close()



#Runs app
if __name__ == "__main__":
    app.run(debug=True, port=8080)