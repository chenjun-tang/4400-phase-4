from flask import Flask, render_template
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route("/home")
def home():
    user_type = "Student"
    user_type = "Tester"
    user_type = "Admin"
    user_type = "Lab Technician"
    user_type = "Lab Technician/Tester"
    return render_template("home.html", user_type = user_type)

@app.route("/aggregate_results")
def aggregate_results():
    return render_template("aggregate_results.html")

if __name__ == '__main__':
    app.run(debug=True)