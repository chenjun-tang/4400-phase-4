from flask import Flask, Response, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, LoginManager, login_required, current_user, login_user,logout_user 
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired
import os
from flaskext.mysql import MySQL
from execSQL import *
from hashlib import md5

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = "4400"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'basic'
login_manager.login_view = '/'
login_manager.login_message = 'Please login.'


mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '88566717'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor =conn.cursor()
cursor.execute("use covidtest_fall2020")
exec_sql_file(cursor, './db_init.sql')
exec_proc_file(cursor, './db_procedure.sql')


# User models
class User(UserMixin):

    def __init__(self,username):
        self.username = username
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False 
    def get_id(self):
        return self.username


class LoginForm(FlaskForm):
    username = StringField('usrname', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField("remember me", default=False)


@login_manager.user_loader
def load_user(username):
    return User(username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# screen 1
@app.route('/',methods=['GET', 'POST'])
def index():
    # next = request.args.get('next')
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = md5(form.password.data.encode('utf-8')).hexdigest()
        remeber_me = form.remember_me.data
        cursor.execute('SELECT * FROM user WHERE username = %s AND user_password = %s', (username, password))
        account = cursor.fetchone()
        
        if not account:
            line = "Invaild username or password!"
            return render_template("index.html", msg=line, form=form)
        else:
            user = User(username)
            login_user(user, remember=form.remember_me.data)
            
            is_student = cursor.execute('SELECT * FROM student WHERE student_username = %s',(username))
            if is_student:
                return redirect(url_for("home", user_type='Student', user_name=username))
            is_admin = cursor.execute('SELECT * FROM administrator WHERE admin_username = %s',(username))
            if is_admin:
                return redirect(url_for("home", user_type='Admin', user_name=username))
            is_labtech = cursor.execute('SELECT * FROM labtech WHERE labtech_username = %s',(username))
            is_sitetester = cursor.execute('SELECT * FROM sitetester WHERE sitetester_username = %s',(username))
            if is_labtech==1 and is_sitetester==1:
                return redirect(url_for("home", user_type='Lab Technician/Tester', user_name=username))
            elif is_labtech==1 and is_sitetester == 0:
                return redirect(url_for("home", user_type='Lab Technician', user_name=username))
            elif is_labtech ==0 and is_sitetester==1:
                return redirect(url_for("home", user_type='Tester', user_name=username))

    return render_template('index.html', form=form)

# screen 2
@app.route("/register", methods=['GET', 'POST'])
def register():
    # do the similar as the function above
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['password']

        if "lab_tech" not in request.form and "site_tester" not in request.form:
            house_type = request.form['housing_type']
            location = request.form['location']
            cursor.execute('CALL register_student(%s,%s,%s,%s,%s,%s,%s)',(username, email, fname, lname, location, house_type, password))
            return redirect(url_for("home", user_type='Student', user_name=username))

        else:
            phone = request.form['phone']
            labtech = "lab_tech" in request.form
            tester = "site_tester" in request.form
            cursor.execute('CALL register_employee(%s,%s,%s,%s,%s,%s,%s,%s)',(username, email, fname, lname, phone, labtech, tester, password))
            if labtech and tester:
                return redirect(url_for("home", user_type='Lab Technician/Tester', user_name=username))
            elif labtech:
                return redirect(url_for("home", user_type='Lab Technician', user_name=username))
            elif tester:
                return redirect(url_for("home", user_type='Tester', user_name=username))

    return render_template('register.html')

# screen 3
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        user_type = request.args.get('user_type')
        user_name = request.args.get('user_name')
    return render_template("home.html", user_type = user_type, user_name = user_name)

# screen 4
@app.route("/student_test_results", methods=['GET','POST'])
@login_required
def student_test_results():
    student_name = request.args.get('user_name')
    if request.method == 'GET':
        cursor.execute('call student_view_results(%s, %s, %s, %s)', (student_name,None, None, None))
        cursor.execute('select * from student_view_results_result')
        data = cursor.fetchall()
        return render_template("student_test_results.html", data_dict = data, user_name = student_name)

    elif request.method == 'POST':
        status = request.form["status"]
        startDate = request.form["startDate"]
        endDate = request.form["endDate"]
        if status == 'all':
            status = None
        if startDate == '':
            startDate = None
        if endDate == '':
            endDate = None

        cursor.execute('call student_view_results(%s, %s, %s, %s)', (student_name, status, startDate, endDate))
        cursor.execute('select * from student_view_results_result')
        data = cursor.fetchall()
        return render_template("student_test_results.html", data_dict = data, user_name = student_name)

    return render_template("student_test_results.html", data_dict = data, user_name=student_name)

#  screen 5
@app.route("/explore_test_result")
@login_required
def explore_test_result():
    if request.method == 'GET':
        user_type = request.args.get('user_type')
        user_name = request.args.get('user_name')
        test_id = request.args.get('test_id')
        if test_id != None:
            cursor.execute('call explore_results(%s)',(test_id))
            cursor.execute('select * from explore_results_result')
            data = cursor.fetchone()
            return render_template("explore_test_result.html", user_type = user_type, user_name = user_name, data = data)
    return render_template("explore_test_result.html", user_type = user_type, user_name = user_name, data = data)


#  screen 6
@app.route("/aggregate_results", methods=['GET','POST'])
@login_required
def aggregate_results():
    cursor.execute('select * from site')
    sites = cursor.fetchall()
    if request.method == 'GET':
        user_type = request.args.get('user_type')
        user_name = request.args.get('user_name')
        cursor.execute('call aggregate_results(null,null,null,null,null);')
        cursor.execute('select * from aggregate_results_result')
        data = cursor.fetchall()
        return render_template("aggregate_results.html", user_type = user_type, user_name = user_name, data=data, sites=sites)

    elif request.method == 'POST':
        user_type = request.args.get('user_type')
        user_name = request.args.get('user_name')
        location = request.form['location']
        housing_type = request.form['housing_type']
        testing_site = request.form['testing_site']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        if location == 'All':
            location = None
        if housing_type == 'All':
            housing_type = None
        if testing_site == 'All':
            testing_site = None
        if len(start_date) == 0:
            start_date = None
        if len(end_date) == 0:
            end_date = None
        # print('call aggregate_results(%s,%s,%s,%s,%s);',(location, housing_type, testing_site,start_date,end_date))

        cursor.execute('call aggregate_results(%s,%s,%s,%s,%s);',(location, housing_type, testing_site,start_date,end_date))
        cursor.execute('select * from aggregate_results_result')
        data = cursor.fetchall()
        return render_template("aggregate_results.html", user_type = user_type, user_name = user_name, data=data, sites=sites)

#  screen 7
@app.route("/sign_up", methods=['GET','POST'])
@login_required
def sign_up():
    if request.method == 'POST':
        #  get user name and list of sites
        user_name = request.args.get('user_name')
        cursor.execute('select * from site')
        sites = cursor.fetchall()

        testing_site = request.form['testing_site']
        startDate = request.form["start_date"]
        endDate = request.form['end_date']
        startTime = request.form['start_time']
        endTime = request.form['end_time']
        cursor.execute('select max(test_id) from test;')
        max_id = cursor.fetchone()
        test_id = int(max_id[0])+1

        if testing_site == 'all':
            testing_site = None
        if len(startDate) == 0:
            startDate = None
        if len(endDate) == 0:
            endDate = None
        if len(startTime) ==0:
            startTime = None
        if len(endTime) == 0:
            endTime = None

        if request.form["action"] == "Signup":
            sign = request.form['sign']
            sign_list = sign.split("+")
            print(sign_list)
            date, time, site_name = sign_list
            print(user_name)
            print(date)
            print(time)
            print(site_name)
            print(test_id)
            cursor.execute('call test_sign_up(%s, %s, %s, %s, %s);', (user_name, site_name, date, time, test_id))
            cursor.execute('call test_sign_up_filter(%s, %s, %s, %s,%s,%s);',
                           (user_name, testing_site, startDate, endDate, startTime, endTime))
            cursor.execute('select * from test_sign_up_filter_result;')
            data = cursor.fetchall()
            return render_template("sign_up.html", data=data, sites=sites, user_name=user_name)
        else:

            cursor.execute('call test_sign_up_filter(%s, %s, %s, %s,%s,%s);', (user_name, testing_site, startDate, endDate, startTime, endTime))
            cursor.execute('select * from test_sign_up_filter_result;')
            data = cursor.fetchall()
            return render_template("sign_up.html", data=data, sites=sites, user_name=user_name)

    else:
        user_name = request.args.get('user_name')
        cursor.execute('select * from site')
        sites = cursor.fetchall()
        cursor.execute('call test_sign_up_filter(%s, null, null, null,null,null);', (user_name))
        cursor.execute('select * from test_sign_up_filter_result;')
        data = cursor.fetchall();
        return render_template("sign_up.html", data=data, sites=sites, user_name=user_name)

#screen 8
@app.route("/labtech_tests_processed",methods=['GET', 'POST'])
@login_required
def labtech_tests_processed():    
    user_type = request.args.get('user_type')
    user_name = request.args.get('user_name')
    if request.method == 'GET':
        cursor.execute('call tests_processed(null,null,null,%s)', user_name)
        cursor.execute('select * from tests_processed_result')
        data = cursor.fetchall()
        return render_template("labtech_tests_processed.html", user_name=user_name, user_type=user_type, data_dict=data)
    
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['testing_result']
        if len(start_date) == 0:
            start_date = None
        if len(end_date) == 0:
            end_date = None
        if status == "all" :
            status = None
        cursor.execute('call tests_processed(%s,%s,%s,%s)', (start_date, end_date, status, user_name))
        cursor.execute('select * from tests_processed_result')
        data = cursor.fetchall()
        return render_template("labtech_tests_processed.html", user_name=user_name, user_type=user_type,  data_dict=data)
        
#screen 9
@app.route("/view_pools", methods=['GET', 'POST'])
@login_required
def view_pools():
    user_type = request.args.get('user_type')
    user_name = request.args.get('user_name')

    if request.method == 'GET':
        cursor.execute('call view_pools(null, null, null, null)')
        cursor.execute('select * from view_pools_result')
        data = cursor.fetchall()

    elif request.method == 'POST':
        processed_by = request.form['processedBy']
        begin_process_date = request.form['start_date']
        end_process_date = request.form['end_date']
        pool_status = request.form['pool_status']
        if pool_status == 'all':
            pool_status = None
        if not begin_process_date or len(begin_process_date) == 0:
            begin_process_date = None
        if not end_process_date or len(end_process_date) == 0:
            end_process_date = None
        cursor.execute('call view_pools(%s, %s, %s, %s)',(begin_process_date, end_process_date, pool_status, processed_by))
        cursor.execute('select * from view_pools_result')
        data = cursor.fetchall()

    return render_template("view_pools.html",user_type = user_type, user_name = user_name, data=data)

# screen 10
@app.route("/create_pool", methods=['GET', 'POST'])
@login_required
def create_pool():
    user_type = request.args.get('user_type')
    user_name = request.args.get('user_name')
    cursor.execute('SELECT test_id, appt_date FROM TEST WHERE pool_id is null')
    data = cursor.fetchall()
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pool_id = request.form['pool_id']
        checkedIDs = []
        for d in data:
            ck = request.form.get(d[0])
            if ck=='on':
                checkedIDs.append(d[0])

        if checkedIDs!=[]:
            test_id = checkedIDs[0]
            cursor.execute('call create_pool(%s,%s)',(pool_id, test_id))
            for i in range(1, len(checkedIDs)):
                test_id = checkedIDs[i]
                cursor.execute('call assign_test_to_pool(%s,%s)',(pool_id, test_id))
                # query again to remove the selected tests in the table
                cursor.execute('SELECT test_id, appt_date FROM TEST WHERE pool_id is null')
                data = cursor.fetchall()

    return render_template("create_pool.html", user_type = user_type, user_name = user_name, data=data)

#screen 11
@app.route("/process_pool", methods=["GET", "POST"])
@login_required
def process_pool():
    user_type = request.args.get('user_type')
    user_name = request.args.get('user_name')
    pool_id = request.args.get('pool_id')
    pool_status = ''
    date = ''
    processed_by = ''
    data = []
    if request.method == 'GET':
        if pool_id:
            cursor.execute('SELECT test_id, appt_date,test_status FROM TEST WHERE pool_id = %s', (pool_id))
            data = cursor.fetchall()

    elif request.method == 'POST':
        if 'status' in request.form:
            pool_status = request.form['status']
        date = request.form['date']
        processed_by = user_name

        if pool_id:
            cursor.execute('SELECT test_id, appt_date,test_status FROM TEST WHERE pool_id = %s', (pool_id))
            data = cursor.fetchall()
        print(pool_id, pool_status, date, processed_by)
        cursor.execute('call process_pool(%s, %s, %s, %s)', (pool_id, pool_status, date, processed_by))
        if pool_status == 'positive':
            for d in data:
                test_id = d[0]
                test_status = request.form[d[0]]
                cursor.execute('call process_test(%s, %s)', (test_id, test_status))
        elif pool_status == 'negative':
            for d in data:
                test_id = d[0]
                test_status = 'negative'
                cursor.execute('call process_test(%s, %s)', (test_id, test_status))
        return redirect(url_for("explore_pool_result", user_type = user_type, user_name = user_name, pool_id = pool_id))
    return render_template("process_pool.html", user_type = user_type, user_name = user_name, pool_id = pool_id, data=data)

# screen 12
@app.route("/create_appointment", methods=["GET", "POST"])
@login_required
def create_appointment():
    user_type = request.args.get('user_type')
    user_name = request.args.get('user_name')
    cursor.execute('select * from site')
    sites = cursor.fetchall()
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        site = request.form['site']
        date = request.form['date']
        time = request.form['time']
        cursor.execute('call create_appointment(%s, %s, %s)',(site, date, time))

    return render_template("create_appointment.html", user_type = user_type, user_name = user_name, sites=sites)

# screen 13
@app.route("/view_appointments", methods=["GET", "POST"])
@login_required
def view_appointments():
    user_type = request.args.get('user_type')
    user_name = request.args.get('user_name')
    cursor.execute('select * from site')
    sites = cursor.fetchall()
    if request.method == 'GET':
        cursor.execute('call view_appointments(null, null, null, null, null, null)')
        cursor.execute('select * from view_appointments_result order by appt_date, appt_time')
        data = cursor.fetchall()
    elif request.method == 'POST':
        user_type = request.args.get('user_type')
        user_name = request.args.get('user_name')
        site = request.form['site']
        s_date = request.form['start_date']
        s_time = request.form['start_time']
        e_date = request.form['end_date']
        e_time = request.form['end_time']
        availablity = request.form['availablity']
        if availablity == 'all':
            availablity = None
        elif availablity == 'booked':
            availablity = 0
        else:
            availablity = 1
        if len(s_date) == 0:
            s_date = None
        if len(e_date) == 0:
            e_date = None
        if len(s_time) == 0:
            s_time = None
        if len(e_time) == 0:
            e_time = None
        cursor.execute('call view_appointments(%s, %s, %s, %s, %s, %s)',(site, s_date, e_date, s_time, e_time, availablity))
        cursor.execute('select * from view_appointments_result')
        data = cursor.fetchall()

    return render_template("view_appointments.html", user_type = user_type, user_name = user_name, sites=sites, data=data)

# screen 14
@app.route("/reassign_tester", methods=["GET", "POST"])
@login_required
def reassign_tester():
    user_type = request.args.get('user_type')
    user_name = request.args.get('user_name')
        
    if request.method == 'POST':
        # how to handle lots of testers at one time
        cursor.execute('SELECT sitetester_username from sitetester')
        testers = cursor.fetchall()

        for tester in testers:
            delete_site = request.form.get("de"+tester[0])
            add_site = request.form.get("add"+tester[0])
            print(tester[0], delete_site, add_site)
            if add_site != None and len(add_site)>0 and add_site != "Not selected":
                cursor.execute('CALL assign_tester(%s,%s)',(tester[0],add_site))
            if delete_site != None and len(delete_site)>0 and delete_site != "Not selected":
                count = cursor.execute('CALL unassign_tester(%s,%s)',(tester[0],delete_site))
    
    cursor.execute('call view_testers()')
    cursor.execute('select * from view_testers_result')
    raw_data = cursor.fetchall()
    data = []
    cursor.execute("select site_name from site")
    all_sites = cursor.fetchall()
    for raw_item in raw_data:
        item = list(raw_item)
        if item[3]:
            item.append(item[3].split(","))
            not_assigned_tests = []
            for site in all_sites:
                if site[0] not in item[4]:
                    not_assigned_tests.append(site[0])
            item.append(not_assigned_tests)
        else:
            item.append(None)
            all_sites_name = []
            for site in all_sites:
                all_sites_name.append(site[0])
            item.append(all_sites_name)
        data.append(item)

    return render_template("reassign_tester.html", data = data, user_type=user_type, user_name = user_name)

# screen 15
@app.route("/create_testing_site", methods=["GET", "POST"])
@login_required
def create_testing_site():
    cursor.execute('select sitetester_username from sitetester')
    testers = cursor.fetchall()
    user_type = request.args.get('user_type')
    user_name = request.args.get('user_name')
    if request.method == 'POST':
        user_type = request.args.get('user_type')
        user_name = request.args.get('user_name')
        site_name = request.form['site']
        street = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zip']
        locaiton = request.form['location']
        tester = request.form['tester']
        print("call create_testing_site(%s, %s, %s, %s, %s, %s, %s)",(site_name,street,city,state,zipcode,locaiton,tester))
        # why cannot insert
        count = cursor.execute("call create_testing_site(%s, %s, %s, %s, %s, %s, %s)",(site_name,street,city,state,zipcode,locaiton,tester))
        print(count)

    return render_template("create_testing_site.html",testers = testers, user_type=user_type, user_name = user_name)

# screen 16
@app.route("/explore_pool_result")
@login_required
def explore_pool_result():
    user_type = request.args.get('user_type')
    user_name = request.args.get('user_name')
    pool_id = request.args.get('pool_id')
    if pool_id != None:
        cursor.execute('call pool_metadata(%s)',(pool_id))
        cursor.execute('select * from pool_metadata_result')
        pool_data = cursor.fetchone()
        cursor.execute('call tests_in_pool(%s)',(pool_id))
        cursor.execute('select * from tests_in_pool_result')
        tests_data = cursor.fetchall()
        return render_template("explore_pool_result.html", user_type = user_type, user_name = user_name, pool_data=pool_data, tests_data=tests_data)

# screen 17
@app.route("/change_testing_site", methods=["GET", "POST"])
@login_required
def change_testing_site():    
    user_name = request.args.get('user_name')
    user_type = request.args.get('user_type')    
    cursor.execute("select fname, lname from user where username = %s",user_name)
    name = cursor.fetchone()
    name = " ".join(name)

    if request.method == 'GET':
        # get the assigned sites
        cursor.execute("CALL tester_assigned_sites(%s)", user_name)
        cursor.execute("select * from tester_assigned_sites_result;")
        sites = cursor.fetchall()
        sites = [s[0] for s in sites]

        cursor.execute("select * from site")
        all_sites = cursor.fetchall()
        all_sites_data = []
        for site in all_sites:
            if (site[0] not in sites):
                all_sites_data.append(site[0])
        return render_template("change_testing_site.html", user_name=user_name, user_type=user_type, name=name, sites=sites,
                               add_sites=all_sites_data)
    else:
        if request.form['add'] == 'None':
            pass
        else:
            site = request.form['add']
            cursor.execute("CALL assign_tester(%s, %s)", (user_name, site))

        if request.form['delete'] == 'None':
            pass;
        else:
            cursor.execute("select count(*) from working_at where username = %s", user_name)

            sites_num = cursor.fetchall()[0][0]
            if sites_num > 1:
                site = request.form['delete']
                cursor.execute("CALL unassign_tester(%s, %s)", (user_name, site))

    cursor.execute("select phone_num from employee where emp_username = %s", user_name)
    phone_num = cursor.fetchall()
    phone_num = phone_num[0][0]

    cursor.execute("CALL tester_assigned_sites(%s)", user_name)
    cursor.execute("select * from tester_assigned_sites_result;")
    sites = cursor.fetchall()

    sites_data = []

    for raw_item in sites:
        sites_data.append(raw_item[0])
    #print(sites_data)

    cursor.execute("select * from site")
    all_sites = cursor.fetchall()
    all_sites_data = []
    for site in all_sites:
        if (site[0] not in sites_data):
            all_sites_data.append(site[0])
    #print(all_sites_data)
    return render_template("change_testing_site.html",user_name = user_name, user_type=user_type, name=name, sites=sites_data,
                           add_sites=all_sites_data)

# screen 18
@app.route("/daily_results")
@login_required
def daily_results():
    user_type = request.args.get('user_type')
    user_name = request.args.get('user_name')
    cursor.execute('call daily_results();')
    cursor.execute('SELECT * FROM daily_results_result;')
    data = cursor.fetchall()
    return render_template("daily_results.html", user_type=user_type, user_name=user_name, data=data)


if __name__ == '__main__':
    app.run(debug=True)
