#!/bin/bash
# Initialize LobsterNotes database

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# MySQL configuration - use environment variables or command detection with defaults
MYSQL_BIN="${MYSQL_BIN:-$(command -v mysql 2>/dev/null || command -v mariadb 2>/dev/null || echo $HOME/mysql/bin/mysql)}"

# Auto-detect socket location (try common MySQL and MariaDB sockets)
SOCKET="${MYSQL_SOCKET:-}"
if [ -z "$SOCKET" ]; then
    socket_paths=(
        "$HOME/mysql.sock"
        "/tmp/mysql.sock"
        "/var/run/mysqld/mysqld.sock"   # MariaDB default
        "/var/run/mysqld/mysql.sock"    # MySQL default
    )
    for path in "${socket_paths[@]}"; do
        if [ -S "$path" ] 2>/dev/null; then
            SOCKET="$path"
            break
        fi
    done
fi

USER="admin"
PASS="admin"
SQL_DIR="$SCRIPT_DIR/sql-commands"
VENV_PATH="$PROJECT_ROOT/lobsterenv/bin/activate"

# Wait for MySQL to be ready
echo "Waiting for MySQL to start..."
for i in {1..30}; do
    # Re-detect socket on each iteration in case MySQL just started
    if [ -z "$SOCKET" ]; then
        for path in "${socket_paths[@]}"; do
            if [ -S "$path" ] 2>/dev/null; then
                SOCKET="$path"
                break
            fi
        done
    fi
    
    if [ -n "$SOCKET" ]; then
        if $MYSQL_BIN -u $USER -p$PASS -S $SOCKET -e "SELECT 1" &>/dev/null; then
            echo "MySQL is ready!"
            break
        fi
    else
        if $MYSQL_BIN -u $USER -p$PASS -h localhost -e "SELECT 1" &>/dev/null; then
            echo "MySQL is ready!"
            break
        fi
    fi
    sleep 1
done

# Build MySQL connection args
if [ -n "$SOCKET" ]; then
    MYSQL_CONN="-S $SOCKET"
else
    MYSQL_CONN="-h localhost"
fi

# Always reinitialize database
echo "Dropping and recreating database..."
# First, get the data directory location
if [ -n "$SOCKET" ]; then
    DATADIR=$($MYSQL_BIN -u $USER -p$PASS -S $SOCKET -sN -e "SELECT @@datadir;" 2>/dev/null)
    # Drop all tables first to allow clean database drop
    $MYSQL_BIN -u $USER -p$PASS -S $SOCKET -e "USE lobsternotes; SET FOREIGN_KEY_CHECKS = 0; DROP TABLE IF EXISTS StageWebData, teaches, enrolled, website, video, image, pdf, note, rating, resource, course, professor, student, user, subject; SET FOREIGN_KEY_CHECKS = 1;" 2>/dev/null
    # Now drop and recreate database
    $MYSQL_BIN -u $USER -p$PASS -S $SOCKET -e "DROP DATABASE IF EXISTS lobsternotes;" 2>&1
    $MYSQL_BIN -u $USER -p$PASS -S $SOCKET -e "CREATE DATABASE lobsternotes;" 2>&1
else
    DATADIR=$($MYSQL_BIN -u $USER -p$PASS -h localhost -sN -e "SELECT @@datadir;" 2>/dev/null)
    # Drop all tables first to allow clean database drop
    $MYSQL_BIN -u $USER -p$PASS -h localhost -e "USE lobsternotes; SET FOREIGN_KEY_CHECKS = 0; DROP TABLE IF EXISTS StageWebData, teaches, enrolled, website, video, image, pdf, note, rating, resource, course, professor, student, user, subject; SET FOREIGN_KEY_CHECKS = 1;" 2>/dev/null
    # Now drop and recreate database
    $MYSQL_BIN -u $USER -p$PASS -h localhost -e "DROP DATABASE IF EXISTS lobsternotes;" 2>&1
    $MYSQL_BIN -u $USER -p$PASS -h localhost -e "CREATE DATABASE lobsternotes;" 2>&1
fi

echo "Creating tables..."
$MYSQL_BIN -u $USER -p$PASS $MYSQL_CONN < "$SQL_DIR/Lobster Notes Tables.sql" 2>&1

echo "Creating indexes..."
$MYSQL_BIN -u $USER -p$PASS $MYSQL_CONN lobsternotes < "$SQL_DIR/Lobster Notes Index Creation.sql" 2>&1

echo "Loading stored procedures and functions..."
# Set library path for mysqlclient
export LD_LIBRARY_PATH="$HOME/mysql/lib:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH" 2>/dev/null
    python3 "$SCRIPT_DIR/load_procedures.py" 2>&1 || echo "Warning: Failed to load procedures via Python"
else
    echo "Warning: Virtual environment not found, stored procedures not loaded"
fi

echo "Importing data..."
$MYSQL_BIN -u $USER -p$PASS $MYSQL_CONN lobsternotes < "$SQL_DIR/Lobster Notes Import Data.sql" 2>&1

echo "Loading constraint validation..."
$MYSQL_BIN -u $USER -p$PASS $MYSQL_CONN lobsternotes < "$SQL_DIR/Constraint Validation.sql" 2>&1

echo "Database initialized successfully!"
