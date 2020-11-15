from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# screen 1
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

# screen 2 
@app.route("/register", methods=['GET', 'POST'])
def register():
    # do the similar as the function above 
    # if request.method == 'POST'
    
    return render_template('register.html')

# screen 3
@app.route("/home", methods=['GET', 'POST'])
def home():
    user_type = "Student"
    user_type = "Tester"
    # user_type = "Admin"
    # user_type = "Lab Technician"
    user_type = "Lab Technician/Tester"
    return render_template("home.html", user_type = user_type)

# screen 4
@app.route("/student_test_results")
def student_test_results():
    return render_template("student_test_results.html")

#  screen 5
@app.route("/explore_test_result")
def explore_test_result():
    return render_template("explore_test_result.html")

#  screen 6
@app.route("/aggregate_results")
def aggregate_results():
    return render_template("aggregate_results.html")

#  screen 7
@app.route("/sign_up")
def sign_up():
    return render_template("sign_up.html")

#screen 8
@app.route("/labtech_tests_processed",methods=['GET', 'POST'])
def labtech_tests_processed():
    # simulate the data
    data = {
        1:['1', '22332','8/17/20','8/29/20','Negative'],
        2:['1', '22332','8/17/20','8/29/20','Negative'],
    }
    return render_template("labtech_tests_processed.html", data_dict=data)

#screen 9
@app.route("/view_pools", methods=['GET', 'POST'])
def view_pools():
    data = {
        1:['23332', '1,2,3','8/17/20','jim123','Negative'],
        2:['2332', '4,5,6','8/17/20','jim456','Negative'],
    }
    return render_template("view_pools.html",data_dict=data)

# screen 10
@app.route("/create_pool")
def create_pool():
    return render_template("create_pool.html")

#screen 11
@app.route("/process_pool", methods=["GET", "POST"])
def process_pool():
    pool_id = 1234
    data = {
        1:['1','8/17/20','Negative'],
        2:['2','8/19/20','Negatve'],
    }
    return render_template("process_pool.html", pool_id = pool_id, data_dict=data)

# screen 12
@app.route("/create_appointment")
def create_appointment():
    return render_template("create_appointment.html")


# screen 15
@app.route("/create_testing_site")
def create_testing_site():
    return render_template("create_testing_site.html")

# screen 18
@app.route("/daily_results")
def daily_results():
    return render_template("daily_results.html")



if __name__ == '__main__':
    app.run(debug=True)