#!/usr/bin/env python3
import MySQLdb
import re

# Connect to MySQL
conn = MySQLdb.connect(
    host='localhost',
    user='admin',
    passwd='admin',
    db='lobsternotes',
    unix_socket='/home/nikki.gorski/mysql.sock'
)

cursor = conn.cursor()

# Read the SQL files
with open('/home/nikki.gorski/databases/cos457_course_proj/sql-commands-and-backend/sql-commands/Lobster Notes Tables.sql', 'r') as f:
    tables_sql = f.read()

with open('/home/nikki.gorski/databases/cos457_course_proj/sql-commands-and-backend/sql-commands/Stored Procedures and Functions.sql', 'r') as f:
    procs_sql = f.read()

# Split into individual statements (procedures/functions end with 'end;')
combined = tables_sql + '\n' + procs_sql

# Find all procedures and functions
pattern = r'(create\s+(procedure|function)\s+\w+.*?end;)'
matches = re.findall(pattern, combined, re.IGNORECASE | re.DOTALL)

for match in matches:
    statement = match[0]
    try:
        cursor.execute(statement)
        print(f"Created {match[1]}: {statement.split()[2]}")
    except Exception as e:
        print(f"Error creating {match[1]}: {e}")

conn.commit()
cursor.close()
conn.close()
print("Stored procedures and functions loaded!")
