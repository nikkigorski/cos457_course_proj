from flask import Flask, request, jsonify, render_template
from flaskext.mysql import MySQL
from markupsafe import escape
from flask_cors import CORS
import pymysql
import re

from pymysql import cursors

'''
todo
-attach to database
-
'''


app = Flask(__name__)
cors = CORS(app,origins='*')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'LobsterNotes'

mysql = MySQL(cursorclass=cursors.DictCursor)
mysql.init_app(app)
cursor = mysql.connect().cursor()
# above is potentially a correct way to get a cursor






@app.route("/")
def index():
    cur = mysql.connect().cursor()
    request.form
    return ("")
# above is another potentially correct way to get a cursor
# same thing is made, difference is this is in a flask function
# apparently necessary??


# practice
@app.route("/api/users",methods=['GET'])
def hello_world():
    return jsonify(
        {
            "users": [
                "me","you","them"
            ]
        }
    )





if __name__ == "__main__":
    app.run(debug=False,port=8080)