#!/usr/bin/env python3
"""
Load Khan Academy scraped data into the Lobster Notes database.
"""
import json
import MySQLdb
import sys
import os

# Get script directory and try common socket paths
script_dir = os.path.dirname(os.path.abspath(__file__))
socket_paths = [
    '/tmp/mysql.sock',
    '/var/run/mysqld/mysql.sock',
    os.path.expanduser('~/mysql.sock'),
]

socket_path = None
for path in socket_paths:
    if os.path.exists(path):
        socket_path = path
        break

# Database connection
conn = MySQLdb.connect(
    host='localhost',
    user='admin',
    passwd='admin',
    db='lobsternotes',
    unix_socket=socket_path if socket_path else '/tmp/mysql.sock'
)

cursor = conn.cursor()

# Load JSON file - relative to script directory
json_file = os.path.join(script_dir, 'backend', 'data-scraping-and-validation', 'oldVersions', 'Scraping scripts', 'data.json')

print(f"Loading data from {json_file}...")

try:
    with open(json_file, 'r') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON file: {e}")
    sys.exit(1)

# Insert into StageWebData table
try:
    # First, ensure default authors exist
    print("Creating default author users if they don't exist...")
    
    # Get all unique author names from the JSON data
    authors = set()
    if 'Resource' in data and isinstance(data['Resource'], list):
        for resource in data['Resource']:
            if isinstance(resource, dict) and 'Author' in resource:
                authors.add(resource['Author'])
    
    # Create user for each unique author if they don't exist
    for author in authors:
        try:
            cursor.execute(
                "INSERT IGNORE INTO User (Name, Courses, IsProfessor) VALUES (%s, NULL, FALSE)",
                (author,)
            )
            if cursor.rowcount > 0:
                # Get the UserID that was just created
                cursor.execute("SELECT UserID FROM User WHERE Name = %s", (author,))
                user_id = cursor.fetchone()[0]
                # Create student entry for this user
                cursor.execute("INSERT INTO Student (UserID) VALUES (%s)", (user_id,))
                print(f"  Created user: {author}")
        except Exception as e:
            print(f"  Warning: Could not create user '{author}': {e}")
    
    conn.commit()
    
    cursor.execute(
        "INSERT INTO StageWebData (WebData, Imported) VALUES (%s, 0)",
        (json.dumps(data),)
    )
    data_id = cursor.lastrowid
    print(f"Inserted data into StageWebData with DataID: {data_id}")
    
    # Call the ImportData stored procedure
    cursor.execute("CALL ImportData(%s)", (data_id,))
    print(f"Called ImportData procedure for DataID: {data_id}")
    
    # Mark as imported
    cursor.execute("UPDATE StageWebData SET Imported = 1 WHERE DataID = %s", (data_id,))
    
    conn.commit()
    print("Khan Academy data import completed successfully!")
    
except Exception as e:
    print(f"Error importing data: {e}")
    conn.rollback()
    sys.exit(1)
finally:
    cursor.close()
    conn.close()
