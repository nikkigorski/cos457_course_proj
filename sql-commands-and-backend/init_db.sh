#!/bin/bash
# Initialize LobsterNotes database

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# MySQL configuration - use environment variables or command detection with defaults
MYSQL_BIN="${MYSQL_BIN:-$(command -v mysql || echo $HOME/mysql/bin/mysql)}"
SOCKET="${MYSQL_SOCKET:-$HOME/mysql.sock}"
USER="admin"
PASS="admin"
SQL_DIR="$SCRIPT_DIR/sql-commands"
VENV_PATH="$PROJECT_ROOT/lobsterenv/bin/activate"

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
export LD_LIBRARY_PATH="$MYSQL_HOME/lib:$LD_LIBRARY_PATH"
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH" 2>/dev/null
    python3 "$SCRIPT_DIR/load_procedures.py"
else
    echo "Warning: Virtual environment not found, skipping Python procedures"
fi

echo "Importing data..."
$MYSQL_BIN -u $USER -p$PASS -S $SOCKET lobsternotes < "$SQL_DIR/Lobster Notes Import Data.sql" 2>&1

echo "Loading constraint validation..."
$MYSQL_BIN -u $USER -p$PASS -S $SOCKET lobsternotes < "$SQL_DIR/Constraint Validation.sql" 2>&1

echo "Database initialized successfully!"
