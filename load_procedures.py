#!/usr/bin/env python3
import MySQLdb
import re
import os

# Get script directory and try common socket paths
script_dir = os.path.dirname(os.path.abspath(__file__))
socket_paths = [
    os.path.expanduser('~/mysql.sock'),
    '/tmp/mysql.sock',
    '/var/run/mysqld/mysqld.sock',  # MariaDB default
    '/var/run/mysqld/mysql.sock',
]

socket_path = None
for path in socket_paths:
    if os.path.exists(path):
        socket_path = path
        break

# Connect to MySQL
conn = MySQLdb.connect(
    host='localhost',
    user='admin',
    passwd='admin',
    db='lobsternotes',
    unix_socket=socket_path if socket_path else '/tmp/mysql.sock'
)

cursor = conn.cursor()

# Read the SQL files - relative to script directory
sql_dir = os.path.join(script_dir, 'sql-commands')
with open(os.path.join(sql_dir, 'Lobster Notes Tables.sql'), 'r') as f:
    tables_sql = f.read()

with open(os.path.join(sql_dir, 'Stored Procedures and Functions.sql'), 'r') as f:
    procs_sql = f.read()

# Only use the procedures file, not the tables file (which has commented procedures)
# Find all procedures and functions
pattern = r'(create\s+(procedure|function)\s+\w+.*?end;)'
matches = re.findall(pattern, procs_sql, re.IGNORECASE | re.DOTALL)

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
