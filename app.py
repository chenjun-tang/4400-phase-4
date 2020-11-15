from flask import Flask, render_template, request, redirect, url_for
import os
#from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL

app = Flask(__name__, template_folder="templates", static_folder="static")

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
#app.config['MYSQL_DATABASE_DB'] = 'Database'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor =conn.cursor()

def exec_sql_file(cursor, sql_file):
    print("\n[INFO] Executing SQL script file: '%s'" % (sql_file))
    statement = ""

    for line in open(sql_file):
        if line.strip().startswith('--'):  # ignore sql comment lines
            continue
        if not line.strip().endswith(';'):  # keep appending lines that don't end in ';'
            statement = statement + line
        else:  # when you get a line ending in ';' then exec statement and reset for next statement
            statement = statement + line
            #print "\n\n[DEBUG] Executing SQL statement:\n%s" % (statement)
            cursor.execute(statement)

            statement = ""
            
exec_sql_file(cursor, './db_init.sql')
cursor.execute("SELECT * FROM STUDENT")
data = cursor.fetchall()
print(data)

#exec_sql_file(cursor, './db_procedure.sql')
cursor.execute("""CREATE PROCEDURE view_testers()
BEGIN
    DROP TABLE IF EXISTS view_testers_result;
    CREATE TABLE view_testers_result(

        username VARCHAR(40),
        name VARCHAR(80),
        phone_number VARCHAR(10),
        assigned_sites VARCHAR(255));

    INSERT INTO view_testers_result
-- Type solution below

    SELECT sitetester_username as username, concat(fname, ' ', lname) as 'name', phone_num as 'phone_number', group_concat(site ORDER BY site ASC) as 'assigned_sites'
    FROM ((SITETESTER JOIN EMPLOYEE ON sitetester_username = emp_username) JOIN USER ON sitetester_username = username) LEFT OUTER JOIN WORKING_AT ON sitetester_username = WORKING_AT.username
    GROUP BY sitetester_username;
-- End of solution
END""")

cursor.callproc('view_testers')
cursor.execute("SELECT * FROM view_testers_result")
data = cursor.fetchall()
print(data)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route("/home", methods=['GET', 'POST'])
def home():
    user_type = "Student"
    user_type = "Tester"
    user_type = "Admin"
    user_type = "Lab Technician"
    # user_type = "Lab Technician/Tester"
    return render_template("home.html", user_type = user_type)

@app.route("/aggregate_results")
def aggregate_results():
    return render_template("aggregate_results.html")

@app.route("/daily_results")
def daily_results():
    return render_template("daily_results.html")

if __name__ == '__main__':
    app.run(debug=True)