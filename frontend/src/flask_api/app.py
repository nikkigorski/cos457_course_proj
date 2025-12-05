#!/usr/bin/env python3
"""Simple Flask REST API for Lobster Notes (MySQL)

Usage (development):
  python3 -m pip install -r requirements.txt
  cp .env.example .env  # edit credentials
  python app.py

Endpoints:
  GET  /api/health
  GET  /api/notes
  GET  /api/notes/<id>
  POST /api/notes
  GET  /api/search?q=...
  GET  /api/dashboard/courses

This uses PyMySQL and simple per-request connections (suitable for dev).
"""

from flask import Flask, g, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import pymysql

load_dotenv()

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'LobsterNotes')
FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', '*')

app = Flask(__name__)
CORS(app, origins=FRONTEND_ORIGIN)


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                               password=DB_PASSWORD, database=DB_NAME,
                               cursorclass=pymysql.cursors.DictCursor,
                               autocommit=False)
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass


@app.route('/api/health')
def health():
    return jsonify({'ok': True})


@app.route('/api/notes')
def list_notes():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT r.ResourceID, r.DateFor AS Date, r.Author, r.Topic AS Title,
                       r.Rating, r.Format
                FROM Resource r
                ORDER BY r.DateFor DESC
                LIMIT 100
            """)
            rows = cur.fetchall()
        return jsonify(rows)
    except Exception as e:
        app.logger.exception('DB error in list_notes')
        return jsonify({'error': 'DB error'}), 500


@app.route('/api/notes/<int:note_id>')
def get_note(note_id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT r.*, n.Body AS NoteBody, p.Link AS PdfLink, i.Link AS ImageLink,
                       w.Link AS WebsiteLink, v.Link AS VideoLink, v.Duration
                FROM Resource r
                LEFT JOIN Note n ON n.ResourceID = r.ResourceID
                LEFT JOIN pdf p ON p.RESOURCEID = r.ResourceID
                LEFT JOIN Image i ON i.ResourceID = r.ResourceID
                LEFT JOIN Website w ON w.ResourceID = r.ResourceID
                LEFT JOIN Video v ON v.ResourceID = r.ResourceID
                WHERE r.ResourceID = %s
                LIMIT 1
            """, (note_id,))
            row = cur.fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(row)
    except Exception:
        app.logger.exception('DB error in get_note')
        return jsonify({'error': 'DB error'}), 500


@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json() or {}
    required = ('Author', 'Topic', 'Format')
    for k in required:
        if k not in data:
            return jsonify({'error': f'missing {k}'}), 400

    db = get_db()
    conn = db
    try:
        with conn.cursor() as cur:
            # Insert resource
            cur.execute(
                "INSERT INTO Resource (DateFor, Author, Topic, Keywords, Format) VALUES (%s, %s, %s, %s, %s)",
                (data.get('DateFor'), data['Author'], data['Topic'], data.get('Keywords'), data['Format'])
            )
            resource_id = cur.lastrowid
            fmt = data['Format']
            if fmt == 'Note':
                cur.execute("INSERT INTO Note (ResourceID, Body) VALUES (%s, %s)", (resource_id, data.get('Body')))
            elif fmt == 'Pdf':
                cur.execute("INSERT INTO pdf (ResourceID, Body, Link) VALUES (%s, %s, %s)", (resource_id, data.get('Body'), data.get('Link')))
            elif fmt == 'Image':
                cur.execute("INSERT INTO Image (ResourceID, Size, Link) VALUES (%s, %s, %s)", (resource_id, data.get('Size'), data.get('Link')))
            elif fmt == 'Website':
                cur.execute("INSERT INTO Website (ResourceID, Link) VALUES (%s, %s)", (resource_id, data.get('Link'),))
            elif fmt == 'Video':
                cur.execute("INSERT INTO Video (ResourceID, Duration, Link) VALUES (%s, %s, %s)", (resource_id, data.get('Duration'), data.get('Link')))
        conn.commit()
        return jsonify({'ResourceID': resource_id}), 201
    except Exception:
        conn.rollback()
        app.logger.exception('DB error in create_note')
        return jsonify({'error': 'DB error'}), 500


@app.route('/api/search')
def search():
    q = (request.args.get('q') or '').strip()
    if not q:
        return jsonify([])
    db = get_db()
    try:
        with db.cursor() as cur:
            # Try fulltext first (if available)
            try:
                cur.execute("""
                    SELECT ResourceID, Topic AS Title, Author, Rating, Format
                    FROM Resource
                    WHERE MATCH(Keywords, Topic) AGAINST (%s IN NATURAL LANGUAGE MODE)
                    LIMIT 100
                """, (q,))
                rows = cur.fetchall()
                if rows:
                    return jsonify(rows)
            except Exception:
                # fulltext may not be available; fallback
                app.logger.debug('Fulltext search failed, falling back to LIKE')

            likeq = f"%{q}%"
            cur.execute("""
                SELECT ResourceID, Topic AS Title, Author, Rating, Format
                FROM Resource
                WHERE Keywords LIKE %s OR Topic LIKE %s
                LIMIT 100
            """, (likeq, likeq))
            rows = cur.fetchall()
        return jsonify(rows)
    except Exception:
        app.logger.exception('DB error in search')
        return jsonify({'error': 'DB error'}), 500


@app.route('/api/dashboard/courses')
def dashboard_courses():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT CourseID, Name, Subject, CatalogNumber, Year FROM Course ORDER BY Year DESC LIMIT 200")
            rows = cur.fetchall()
        return jsonify(rows)
    except Exception:
        app.logger.exception('DB error in dashboard_courses')
        return jsonify({'error': 'DB error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', '4000'))
    app.run(host='0.0.0.0', port=port, debug=True)
