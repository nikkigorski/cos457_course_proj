#!/usr/bin/env python3
"""
Simple loader for Khan Academy data that directly loads from JSON to DB
"""
import json
import MySQLdb
import sys
import os

# Get script directory and try common socket paths
script_dir = os.path.dirname(os.path.abspath(__file__))
socket_paths = [
    os.path.expanduser('~/mysql.sock'),
    '/tmp/mysql.sock',
    '/var/run/mysqld/mysqld.sock',
    '/var/run/mysqld/mysql.sock',
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

# Load JSON file
json_file = os.path.join(script_dir, 'backend', 'data-scraping-and-validation', 'oldVersions', 'Scraping scripts', 'data.json')

print(f"Loading data from {json_file}...")

try:
    with open(json_file, 'r') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON file: {e}")
    sys.exit(1)

try:
    # Ensure author exists
    author = 'khan accademy, lobster notes web scraper'
    cursor.execute("INSERT IGNORE INTO user (Name, Password, IsProfessor) VALUES (%s, %s, FALSE)", 
                   (author, 'khan123'))
    conn.commit()
    
    # Build lookup maps for detail data
    notes_map = {item['ResourceID']: item for item in data.get('Note', [])}
    videos_map = {item['ResourceID']: item for item in data.get('Video', [])}
    images_map = {item['ResourceID']: item for item in data.get('Image', [])}
    websites_map = {item['ResourceID']: item for item in data.get('Website', [])}
    pdfs_map = {item['ResourceID']: item for item in data.get('pdf', [])}
    
    inserted_count = 0
    skipped_count = 0
    
    # Process each resource
    for resource in data.get('Resource', []):
        try:
            rid = resource['ResourceID']
            date_str = resource.get('Date', '2025-12-06')
            date_for = resource.get('DateFor', '2025-12-06')
            author_name = resource.get('Author', author)
            topic = resource.get('Topic', 'n/a')[:25]  # Truncate to 25 chars
            keywords = resource.get('Keywords')
            if keywords:
                keywords = keywords[:25]
            format_type = resource.get('Format', 'Note').lower()
            rating = resource.get('Rating', 3.0)
            
            # Skip if invalid format
            valid_formats = ['note', 'video', 'image', 'website', 'pdf']
            if format_type not in valid_formats:
                skipped_count += 1
                continue
            
            # Insert main resource
            cursor.execute(
                """INSERT INTO resource (ResourceID, Date, DateFor, Author, Topic, Keywords, Format, Rating, isVerified)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0)""",
                (rid, date_str, date_for, author_name, topic, keywords, format_type, rating)
            )
            
            # Insert type-specific data
            if format_type == 'note' and rid in notes_map:
                body = notes_map[rid].get('Body', '')[:2048]
                cursor.execute(
                    "INSERT IGNORE INTO note (ResourceID, Body) VALUES (%s, %s)",
                    (rid, body)
                )
            elif format_type == 'video' and rid in videos_map:
                video = videos_map[rid]
                duration = video.get('Duration', 0)
                link = video.get('Link', '')
                cursor.execute(
                    "INSERT IGNORE INTO video (ResourceID, Duration, Link) VALUES (%s, %s, %s)",
                    (rid, duration, link)
                )
            elif format_type == 'image' and rid in images_map:
                image = images_map[rid]
                size = image.get('Size', 1000)
                link = image.get('Link', '')
                cursor.execute(
                    "INSERT IGNORE INTO image (ResourceID, Size, Link) VALUES (%s, %s, %s)",
                    (rid, size, link)
                )
            elif format_type == 'website' and rid in websites_map:
                link = websites_map[rid].get('Link', '')
                cursor.execute(
                    "INSERT IGNORE INTO website (ResourceID, Link) VALUES (%s, %s)",
                    (rid, link)
                )
            elif format_type == 'pdf' and rid in pdfs_map:
                pdf = pdfs_map[rid]
                body = pdf.get('Body', '')[:2048] if pdf.get('Body') else None
                link = pdf.get('Link', '')
                cursor.execute(
                    "INSERT IGNORE INTO pdf (ResourceID, Body, Link) VALUES (%s, %s, %s)",
                    (rid, body, link)
                )
            
            inserted_count += 1
            
        except Exception as e:
            print(f"  Error inserting resource {rid}: {e}")
            skipped_count += 1
            continue
    
    conn.commit()
    print(f"Khan Academy data import completed!")
    print(f"  Inserted: {inserted_count}")
    print(f"  Skipped: {skipped_count}")
    
except Exception as e:
    print(f"Error importing data: {e}")
    conn.rollback()
    sys.exit(1)
finally:
    cursor.close()
    conn.close()
