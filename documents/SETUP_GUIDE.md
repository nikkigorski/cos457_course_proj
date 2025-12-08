# Lobster Notes Project Setup Guide
**Project**: cos457_course_proj (Database & Web Application)  
**Team**: Nikki Gorski, Gage White, Jove Emmons, Gabrielle Akers

---

## System Requirements


### Software
- **Python 3.8+**: Core language for scraper and backend
- **Node.js 16+**: Required for React/Vite frontend
- **MySQL 8.0+**: Database server
- **git**: Version control
- **bash**: Shell environment (default on Linux)

### Browser (for web app)
- **Chrome/Chromium**: Required for Selenium web scraping
- **Modern browser** (Chrome, Firefox, Safari): For frontend access

### Optional but Recommended
- **Visual Studio Code**: Editor with extensions for Python, JavaScript
- **MySQL Workbench**: GUI for database exploration
- **curl/Postman**: API testing tools

---

## Initial Setup

### 1. Clone the Repository

```bash
cd ~
git clone https://github.com/nikkigorski/cos457_course_proj.git
cd cos457_course_proj
```

### 2. Check System Environment

```bash
# Verify Python 3 is installed
python3 --version  # Should be 3.8+

# Verify Node.js is installed
node --version    # Should be 16+
npm --version     # Should be 7+

# Verify MySQL socket path exists (set up by admin)
ls -la ~/mysql.sock
```

### 3. Set Environment Variables (Optional)

If your MySQL socket is at a non-standard location, you may need to set:

```bash
export MYSQL_SOCKET="/home/$(whoami)/mysql.sock"
export MYSQL_USER="admin"
export MYSQL_PASS="admin"
export MYSQL_DB="lobsternotes"
```

Add to `~/.bashrc` to persist across sessions:

```bash
echo 'export MYSQL_SOCKET="/home/$(whoami)/mysql.sock"' >> ~/.bashrc
source ~/.bashrc
```

---

## Database Setup

### 1. Ensure MySQL is Running

```bash
# Check if MySQL socket exists and is accessible
ls -S ~/mysql.sock

# If MySQL is not running, start it (admin command)
# ~/mysql/bin/mysqld --datadir=~/mysql-data-lobster --socket=~/mysql.sock &
```

### 2. Create Database and Load Schema

```bash
# Navigate to project root
cd ~/databases/cos457_course_proj

# Run the install script (loads tables, indexes, stored procedures)
./install
```

**What the `install` script does:**
- ✅ Checks for Python 3 and Node.js availability
- ✅ Creates Python virtual environment (`venv`) if missing
- ✅ Installs Python packages from `requirements.txt` (Flask, MySQLdb, Selenium, etc.)
- ✅ Installs Node.js packages from `frontend/package.json` (React, Vite, etc.)
- ✅ Reports successful/failed installations with color-coded output
- ✅ Continues on errors (graceful degradation) rather than hard exit

### 3. Load Initial Data (Optional)

If you want to skip web scraping and use pre-scraped data:

```bash
cd ~/databases/cos457_course_proj/sql-commands-and-backend/backend/data-scraping-and-validation

# Load from existing JSON (if data.json exists)
python3 load_procedures.py

# Or load from SQL dump (if available)
mysql -u admin -padmin -S ~/mysql.sock lobsternotes < backup.sql
```

---

## Data Pipeline: Web Scraping to Database

The data pipeline converts Khan Academy course pages → JSON → MySQL database.

### Pipeline Overview

```
Khan Academy URLs
    ↓
[Selenium WebDriver] → Extract videos, PDFs, images
    ↓
[BeautifulSoup] → Parse HTML, extract metadata
    ↓
[yt-dlp] → Fetch YouTube video metadata
    ↓
Raw JSON (scraped_data.json)
    ↓
[write_json()] → Convert to database schema format
    ↓
Database JSON (data.json)
    ↓
[MySQL LOAD DATA] or [Python insert]
    ↓
MySQL Database (Resource, Note, Video, Image, Website, PDF tables)
```

### Step 1: Prepare Web Scraper

```bash
cd ~/databases/cos457_course_proj/sql-commands-and-backend/backend/data-scraping-and-validation/oldVersions/Scraping\ scripts

# Inspect the scraper code
cat khan_scraper.py
```

**Key scraper components:**

| Component | Purpose |
|-----------|---------|
| `process_single_url(driver_vid, url)` | Extracts videos, PDFs, images from a single course URL |
| `get_image_dimensions(driver, image_url)` | Fetches image width/height via Selenium |
| `write_json()` | Converts raw scraped data to MySQL schema format |
| `main()` | Orchestrates scraping of multiple URLs |

**Important**: The scraper reuses a single Selenium WebDriver to avoid nesting issues:
```python
driver_vid = webdriver.Chrome(...)  # Create once
for url in urls:
    process_single_url(driver_vid, url)  # Pass existing driver
    write_json()  # Convert to DB format
```

### Step 2: Prepare URLs for Scraping

Create a `links.csv` file with Khan Academy course page URLs:

```bash
cat > links.csv << 'EOF'
https://www.khanacademy.org/science/physics/forces-newtons-laws
https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:equations-and-inequalities
EOF
```

### Step 3: Run the Scraper

```bash
# Activate Python virtual environment
cd ~/databases/cos457_course_proj
source venv/bin/activate

# Run scraper
cd sql-commands-and-backend/backend/data-scraping-and-validation/oldVersions/Scraping\ scripts
python3 khan_scraper.py

# Output: data.json (ready for database import)
```

**What the scraper does:**

1. **Initialize WebDriver**: Opens headless Chrome browser
2. **Loop through URLs**: For each URL in links.csv:
   - Navigate to course page
   - Extract all video links (via `<a>` tags)
   - Extract all PDF/image links
   - Call `get_image_dimensions()` for each image (returns width/height)
   - Store in temporary JSON structure
3. **Convert to DB schema**: `write_json()` transforms raw data:
   - Raw: `{"url": "...", "title": "...", "videos": [...]}`
   - Converted: MySQL table format (Resource, Video, Website, Image, PDF)
4. **Accumulate across URLs**: Merges data from all URLs into single `data.json`

**Output files:**
- `data.json`: Final database-ready JSON
- `t2.json`: Temporary file (cleaned up after processing)
- `scraped_data.json`: Raw scraped data (before DB schema conversion)

### Step 4: Import Data into MySQL

```bash
cd ~/databases/cos457_course_proj

# Option A: Use Python import script
python3 sql-commands-and-backend/backend/data-scraping-and-validation/import_data.py

# Option B: Direct MySQL LOAD DATA (faster for large files)
mysql -u admin -padmin -S ~/mysql.sock lobsternotes << 'EOF'
LOAD DATA LOCAL INFILE 'data.json'
INTO TABLE Resource
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
(ResourceID, Topic, Format, DateFor, Author, Keywords);
EOF
```

### Scraper Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `No Chrome/Chromium` | WebDriver missing | `sudo apt-get install chromium` |
| `Selenium timeout` | Page load slow | Increase `WebDriverWait(driver, 20)` timeout |
| `NoneType in write_json()` | Missing field in HTML | Add null checks: `if title: ...` |
| `IndexError: videos list` | Page structure changed | Update selectors in `process_single_url()` |

---

## Backend Setup & Installation

### 1. Understand the Install Script

The `install` script in the project root automates both backend and frontend setup:

```bash
#!/bin/bash
# Checks for Python 3 and Node.js
# Creates venv if needed (python3 -m venv venv)
# Installs packages line-by-line from requirements.txt
# Handles errors gracefully (logs errors, continues)
```

**Under the hood:**

```bash
# Check for Python
which python3

# Create virtual environment (isolated Python environment)
python3 -m venv venv
# → Creates ~/databases/cos457_course_proj/venv/
# → Contains isolated pip packages, Python interpreter

# Activate venv
source venv/bin/activate
# → Modifies $PATH to use venv's Python first
# → All 'pip install' commands now install to venv/, not system

# Install packages
while read package; do
    pip install "$package"
done < requirements.txt
# → Reads each line from requirements.txt
# → Installs Flask, MySQLdb, BeautifulSoup, Selenium, yt-dlp, etc.
# → Skips already-installed packages
```

### 2. Manual Backend Setup (if needed)

```bash
cd ~/databases/cos457_course_proj

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# Installs:
# - Flask 3.0.0 (web framework)
# - Flask-MySQLdb 2.0.0 (MySQL connector)
# - MySQLdb 2.2.0 (raw MySQL client)
# - BeautifulSoup 4.12.2 (HTML parsing)
# - Selenium 4.15.2 (web scraping)
# - yt-dlp 2023.11.16 (YouTube metadata)
# - lxml 4.9.3 (XML parsing)
# - soupsieve 2.5 (CSS selectors)
```

### 3. Verify Backend Setup

```bash
# Activate venv
source venv/bin/activate

# Test Flask
python3 -c "import flask; print(flask.__version__)"
# Output: 3.0.0

# Test MySQL connection
python3 -c "import MySQLdb; conn = MySQLdb.connect(host='localhost', user='admin', passwd='admin', db='lobsternotes', unix_socket='/home/nikki.gorski/mysql.sock'); print('Connected!')"

# Test Selenium
python3 -c "from selenium import webdriver; print('Selenium OK')"
```

### 4. Run Backend Server

```bash
cd ~/databases/cos457_course_proj/Phase\ 3/backend

# Make sure venv is activated
source ../../venv/bin/activate

# Run Flask development server
python3 app.py
# Output:
# * Running on http://127.0.0.1:5000
# * WARNING: Do not use the development server in a production environment.

# The server now accepts API requests at http://localhost:5000/search, /notes, etc.
```

---

## Frontend Setup & Installation

### 1. Understand Node.js Package Installation

The `install` script handles frontend setup via npm:

```bash
# In project root
npm install
# → Reads frontend/package.json
# → Downloads React 18.2.0, Vite, axios, etc.
# → Creates node_modules/ directory (~500 MB)
# → Creates package-lock.json (lockfile for reproducible installs)
```

### 2. Manual Frontend Setup (if needed)

```bash
cd ~/databases/cos457_course_proj/frontend

# Install dependencies
npm install
# Installs:
# - React 18.2.0 (UI library)
# - Vite (build tool & dev server)
# - axios (HTTP client for API calls)
# - react-router-dom (client-side routing)
# - Other dependencies from package.json

# Verify installation
npm list react
# Output: react@18.2.0
```

### 3. Frontend Project Structure

```
frontend/
├── src/
│   ├── App.jsx              # Main app component
│   ├── pages/
│   │   ├── SearchPage.jsx   # Resource search (calls /search API)
│   │   ├── NotePage.jsx     # Resource details (calls /notes API)
│   │   └── HomePage.jsx
│   ├── components/
│   │   ├── SearchBar.jsx    # Search input
│   │   └── ResourceList.jsx # Display results
│   └── main.jsx             # React entry point
├── vite.config.js           # Build configuration
├── package.json             # Dependencies (React, Vite, axios)
└── index.html               # HTML template
```

### 4. Understand Vite

**Vite** is a modern build tool that replaces Webpack:

```bash
# Development mode (hot reload, no build)
npm run dev
# → Starts dev server on http://localhost:5173
# → Watches for file changes, hot-reloads browser
# → Fast iteration during development

# Production build
npm run build
# → Bundles React code into optimized dist/
# → Minifies, tree-shakes unused code
# → Output: dist/index.html, dist/assets/*.js, dist/assets/*.css
```

### 5. Run Frontend Development Server

```bash
cd ~/databases/cos457_course_proj/frontend

npm run dev
# Output:
# VITE v4.5.0 ready in 512 ms
# 
# ➜  Local:   http://127.0.0.1:5173/
# ➜  Press h to show help

# Open http://localhost:5173 in browser
```

---

## Running the Application

### Full Stack (Database + Backend + Frontend)

**Terminal 1: Start MySQL** (if not already running)
```bash
cd ~
./mysql/bin/mysqld --datadir=./mysql-data-lobster --socket=./mysql.sock &
# MySQL runs in background, accessible via socket
```

**Terminal 2: Start Backend API**
```bash
cd ~/databases/cos457_course_proj
source venv/bin/activate
cd Phase\ 3/backend
python3 app.py
# Backend server on http://localhost:5000
```

**Terminal 3: Start Frontend Dev Server**
```bash
cd ~/databases/cos457_course_proj/frontend
npm run dev
# Frontend dev server on http://localhost:5173
```

**Terminal 4: Open in Browser**
```bash
# Open http://localhost:5173
# - SearchPage: Search resources by topic/author
# - NotePage: View resource details and ratings
```

### API Endpoints

| Endpoint | Method | Purpose | Backend Code |
|----------|--------|---------|--------------|
| `/search?topic=X` | GET | Search resources by topic | `Phase 3/backend/app.py` |
| `/search?author=X` | GET | Search resources by author | `Phase 3/backend/app.py` |
| `/notes?id=X` | GET | Get resource details + notes | `Phase 3/backend/app.py` |
| `/rate` | POST | Submit resource rating | `Phase 3/backend/app.py` |

### Example Usage

```bash
# Search for resources with topic "Physics"
curl "http://localhost:5000/search?topic=Physics"
# Output: [{"ResourceID": 123, "Topic": "Physics", ...}]

# Get resource details
curl "http://localhost:5000/notes?id=123"
# Output: {"ResourceID": 123, "Title": "...", "Body": "...", "AvgScore": 4.5}
```

---

## Troubleshooting

### MySQL Connection Issues

**Error**: `Can't connect to MySQL server`

```bash
# Check if MySQL is running
ps aux | grep mysqld

# Check if socket exists
ls -la ~/mysql.sock

# Check socket permissions
chmod 777 ~/mysql.sock

# Verify connection manually
~/mysql/bin/mysql -u admin -padmin -S ~/mysql.sock -e "SELECT 1;"
```

### Flask Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'flask'`

```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall Flask
pip install Flask==3.0.0

# Verify
python3 -c "import flask; print(flask.__version__)"
```

### React Frontend Won't Load

**Error**: `localhost:5173 refused to connect`

```bash
# Check if Vite dev server is running
cd frontend
npm run dev

# Check if port 5173 is in use
lsof -i :5173
# If in use, kill: kill -9 <PID>
```

### Selenium Scraper Crashes

**Error**: `chrome not found` or `WebDriver timeout`

```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser

# Or verify PATH
which chromium

# Update chromedriver-linux64 path in khan_scraper.py
export PATH="$PATH:/home/nikki.gorski/bin/chromedriver-linux64"
```

### Data Not Appearing in Search

**Issue**: Data imported but not visible in SearchPage

```bash
# Check if data was actually imported
mysql -u admin -padmin -S ~/mysql.sock lobsternotes -e "SELECT COUNT(*) FROM Resource;"

# Check if Flask API is returning data
curl "http://localhost:5000/search?topic=test"

# Check React console for errors (F12 → Console)
```

---

## Project Structure

```
cos457_course_proj/
├── README.md                              # Project overview
├── SETUP_GUIDE.md                         # This file
├── QUERY_OPTIMIZATION_REPORT.md           # Query optimization analysis
├── PERFORMANCE_ANALYSIS.md                # Performance tuning guide
├── install                                # Automated setup script
├── requirements.txt                       # Python dependencies
│
├── Phase 3/
│   └── backend/
│       ├── app.py                         # Flask API server
│       ├── database.py                    # MySQL connection
│       └── routes.py                      # API endpoint handlers
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── SearchPage.jsx             # Resource search UI
│   │   │   └── NotePage.jsx               # Resource details UI
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json                       # Node.js dependencies
│   ├── vite.config.js                     # Build configuration
│   └── index.html
│
├── sql-commands-and-backend/
│   ├── sql-commands/
│   │   ├── Lobster Notes Tables.sql       # Table schemas
│   │   ├── Lobster Notes Index Creation.sql # Indexes (optimized)
│   │   └── Stored Procedures and Functions.sql
│   │
│   └── backend/
│       ├── data-scraping-and-validation/
│       │   ├── import_data.py             # Import JSON → MySQL
│       │   └── oldVersions/
│       │       └── Scraping scripts/
│       │           ├── khan_scraper.py    # Web scraper (Selenium)
│       │           └── links.csv          # URLs to scrape
│       │
│       └── load_procedures.py             # Load stored procedures
│
└── venv/                                  # Python virtual environment (created by install)
    └── lib/python3.8/site-packages/       # Installed packages (Flask, MySQLdb, etc.)
```

---

## Key Files Explained

| File | Purpose | What It Does |
|------|---------|--------------|
| `install` | Automated setup | Creates venv, installs Python + Node packages |
| `requirements.txt` | Python dependencies | Lists Flask, MySQLdb, Selenium versions |
| `Phase 3/backend/app.py` | Flask API | Handles HTTP requests, queries database |
| `frontend/package.json` | Node.js dependencies | Lists React, Vite, axios versions |
| `sql-commands-and-backend/sql-commands/Lobster Notes Tables.sql` | Database schema | CREATE TABLE statements |
| `sql-commands-and-backend/sql-commands/Lobster Notes Index Creation.sql` | Query optimization | CREATE INDEX statements (3 composite indexes) |
| `khan_scraper.py` | Data extraction | Selenium-based web scraper |

---

## Common Workflows

### Workflow 1: Fresh Install from Scratch

```bash
# 1. Clone repository
git clone https://github.com/nikkigorski/cos457_course_proj.git
cd cos457_course_proj

# 2. Run automated setup
./install
# This installs everything: venv, Python packages, Node packages, MySQL tables

# 3. Start MySQL (if not running)
cd ~
./mysql/bin/mysqld --datadir=./mysql-data-lobster --socket=./mysql.sock &

# 4. Start backend and frontend
cd ~/databases/cos457_course_proj
source venv/bin/activate
cd Phase\ 3/backend && python3 app.py &  # Background
cd ../../frontend && npm run dev          # Foreground
```

### Workflow 2: Add New Data via Web Scraping

```bash
# 1. Prepare URLs
echo "https://example.com/course1" > links.csv
echo "https://example.com/course2" >> links.csv

# 2. Run scraper
cd sql-commands-and-backend/backend/data-scraping-and-validation/oldVersions/Scraping\ scripts
source ../../../venv/bin/activate
python3 khan_scraper.py
# Output: data.json

# 3. Import into database
python3 ../import_data.py
# Or: mysql ... < data.sql

# 4. Verify in web UI
# Visit http://localhost:5173 → SearchPage → Search for new resources
```

### Workflow 3: Optimize a Slow Query

```bash
# 1. Identify slow query (from logs or user feedback)
# Example: "Search by author takes 5 seconds"

# 2. Run EXPLAIN ANALYZE
mysql -u admin -padmin -S ~/mysql.sock lobsternotes
EXPLAIN ANALYZE SELECT * FROM Resource WHERE Author = 'X' ORDER BY DateFor DESC;

# 3. Add index (or optimize existing)
CREATE INDEX IX_Resource_Author_DateFor ON Resource (Author ASC, DateFor DESC);

# 4. Re-run EXPLAIN ANALYZE to verify improvement
EXPLAIN ANALYZE SELECT * FROM Resource WHERE Author = 'X' ORDER BY DateFor DESC;

# 5. Document in QUERY_OPTIMIZATION_REPORT.md
```

---

## Next Steps

1. **Complete initial setup**: Run `./install` from project root
2. **Start MySQL**: Ensure ~/mysql.sock is accessible
3. **Scrape data** (optional): Use khan_scraper.py to populate database
4. **Run the app**: Start backend + frontend, open http://localhost:5173
5. **Explore queries**: Use curl or Postman to test API endpoints
6. **Check optimization**: Review QUERY_OPTIMIZATION_REPORT.md and PERFORMANCE_ANALYSIS.md

---

## Further Reading

- **Query Optimization**: See `QUERY_OPTIMIZATION_REPORT.md` (before/after EXPLAIN ANALYZE)
- **Performance Tuning**: See `PERFORMANCE_ANALYSIS.md` (index strategy, scalability, monitoring)
- **Database Schema**: See `sql-commands-and-backend/sql-commands/Lobster Notes Tables.sql`
- **Stored Procedures**: See `sql-commands-and-backend/sql-commands/Stored Procedures and Functions.sql`

---

## Support

**For issues or questions**:
- Check **Troubleshooting** section above
- Review **QUERY_OPTIMIZATION_REPORT.md** for query-related issues
- Review **PERFORMANCE_ANALYSIS.md** for performance/scalability questions
- Inspect logs: `~/mysql-data-lobster/error.log`, browser console (F12), Flask terminal output
