#!/bin/bash
source /home/nikki.gorski/databases/cos457_course_proj/lobsterenv/bin/activate
export LD_LIBRARY_PATH=/home/nikki.gorski/mysql/lib:$LD_LIBRARY_PATH
python3 app.py
