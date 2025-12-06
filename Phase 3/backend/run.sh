#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Activate virtual environment if it exists
if [ -f "$PROJECT_ROOT/lobsterenv/bin/activate" ]; then
    source "$PROJECT_ROOT/lobsterenv/bin/activate"
fi

# Set LD_LIBRARY_PATH if mysql lib exists
if [ -d "$PROJECT_ROOT/../mysql/lib" ]; then
    export LD_LIBRARY_PATH="$PROJECT_ROOT/../mysql/lib:$LD_LIBRARY_PATH"
fi

python3 app.py