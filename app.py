from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # print(username)

        # we can now get the username and password here
        # after checking, we need to find the user type and redirect to home
        if True:
            return redirect(url_for("home"))
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    # do the similar as the function above 
    # if request.method == 'POST'
    
    return render_template('register.html')

@app.route("/home", methods=['GET', 'POST'])
def home():
    user_type = "Student"
    user_type = "Tester"
    # user_type = "Admin"
    # user_type = "Lab Technician"
    user_type = "Lab Technician/Tester"
    return render_template("home.html", user_type = user_type)

@app.route("/student_test_results")
def student_test_results():
    return render_template("student_test_results.html")

@app.route("/aggregate_results")
def aggregate_results():
    return render_template("aggregate_results.html")

@app.route("/explore_test_result")
def explore_test_result():
    return render_template("explore_test_result.html")

@app.route("/sign_up")
def sign_up():
    return render_template("sign_up.html")

@app.route("/create_appointment")
def create_appointment():
    return render_template("create_appointment.html")

@app.route("/create_testing_site")
def create_testing_site():
    return render_template("create_testing_site.html")

@app.route("/daily_results")
def daily_results():
    return render_template("daily_results.html")

#screen 8
@app.route("/labtech_tests_processed",methods=['GET', 'POST'])
def labtech_tests_processed():
    # simulate the data
    data = {
        1:['1', '22332','8/17/20','8/29/20','Negative'],
        2:['1', '22332','8/17/20','8/29/20','Negative'],
    }
    return render_template("labtech_tests_processed.html", data_dict=data)

@app.route("/view_pools", methods=['GET', 'POST'])
def view_pools():
    data = {
        1:['23332', '1,2,3','8/17/20','jim123','Negative'],
        2:['2332', '4,5,6','8/17/20','jim456','Negative'],
    }
    return render_template("view_pools.html",data_dict=data)



if __name__ == '__main__':
    app.run(debug=True)