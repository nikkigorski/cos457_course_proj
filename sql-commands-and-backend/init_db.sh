#!/bin/bash
# Initialize LobsterNotes database

MYSQL_BIN="/home/nikki.gorski/mysql/bin/mysql"
SOCKET="/home/nikki.gorski/mysql.sock"
USER="admin"
PASS="admin"
SQL_DIR="/home/nikki.gorski/databases/cos457_course_proj/sql-commands-and-backend/sql-commands"

# Wait for MySQL to be ready
echo "Waiting for MySQL to start..."
for i in {1..30}; do
    if $MYSQL_BIN -u $USER -p$PASS -S $SOCKET -e "SELECT 1" &>/dev/null; then
        echo "MySQL is ready!"
        break
    fi
    sleep 1
done

# Always reinitialize database
echo "Dropping and recreating database..."
$MYSQL_BIN -u $USER -p$PASS -S $SOCKET -e "DROP DATABASE IF EXISTS lobsternotes; CREATE DATABASE lobsternotes;" 2>&1

echo "Creating tables..."
$MYSQL_BIN -u $USER -p$PASS -S $SOCKET lobsternotes < "$SQL_DIR/Lobster Notes Tables.sql" 2>&1

echo "Creating indexes..."
$MYSQL_BIN -u $USER -p$PASS -S $SOCKET lobsternotes < "$SQL_DIR/Lobster Notes Index Creation.sql" 2>&1

echo "Loading stored procedures and functions..."
export LD_LIBRARY_PATH=/home/nikki.gorski/mysql/lib
source /home/nikki.gorski/databases/cos457_course_proj/lobsterenv/bin/activate
python3 /home/nikki.gorski/databases/cos457_course_proj/sql-commands-and-backend/load_procedures.py

echo "Importing data..."
$MYSQL_BIN -u $USER -p$PASS -S $SOCKET lobsternotes < "$SQL_DIR/Lobster Notes Import Data.sql" 2>&1

echo "Loading constraint validation..."
$MYSQL_BIN -u $USER -p$PASS -S $SOCKET lobsternotes < "$SQL_DIR/Constraint Validation.sql" 2>&1

echo "Database initialized successfully!"
