from flask import Flask,render_template,redirect,request,session,url_for,send_file,flash,Response,make_response
from flask_mysqldb import MySQL
from flask_toastr import Toastr
from flask_mail import *
from functools import wraps
import pandas as pd
import datetime
import csv
import io
import json
import os
import csv
import xlwt
from passlib.hash import sha256_crypt
from wtforms import Form,StringField,TextAreaField,PasswordField,validators


print(os.environ.get('MYSQL_HOST', None))

app=Flask(__name__)
# app.config['MYSQL_HOST']=os.environ.get('MYSQL_HOST', None)
# app.config['MYSQL_USER']=os.environ.get('MYSQL_USER', None)
# app.config['MYSQL_PASSWORD']=os.environ.get('MYSQL_PASSWORD', None)
# app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', None)
# app.config['SECRET_KEY']=os.environ.get('SECRET_KEY', None)
# app.config['MySQL_CURSORCLASS']=os.environ.get('MySQL_CURSORCLASS', None)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='UPGRAD'
app.config['MYSQL_DB'] = ''
app.config['SECRET_KEY']='5fac8abdefb2af8f4f700758739e3189'
app.config['MySQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)
toastr = Toastr()
toastr.init_app(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']='465'
app.config['MAIL_USE_SSL']=True
app.config['MAIL_DEBUG']=True
app.config['MAIL_USERNAME']='drives@upgrad.com'
app.config['MAIL_PASSWORD']='upGrad2021@Drives'
app.config['MAIL_ASCII_ATTACHMENTS']=True
# app.config['MAIL_SERVER']=os.environ.get('MAIL_SERVER', None)
# app.config['MAIL_PORT']=os.environ.get('MAIL_PORT', None)
# app.config['MAIL_USE_SSL']=False
# app.config['MAIL_DEBUG']=True
# app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME', None)
# app.config['MAIL_PASSWORD']=os.environ.get('MAIL_PASSWORD', None)
# app.config['MAIL_ASCII_ATTACHMENTS']=True
mail=Mail(app)
def getLoginDetails():
    cur = mysql.connection.cursor()
    if 'email' not in session:
        loggedIn = False
        email = ''
    else:
        loggedIn = True
        cur.execute("SELECT userid,email FROM user WHERE email = '" + session['email'] + "'")
        userid, email = cur.fetchone()
       # cur.execute("SELECT count(prod_id) FROM cart WHERE id = " + str(id))
        #noOfItems = cur.fetchone()[0]
    cur.close()
    return (loggedIn,email)

class RegisteredForm(Form):
    fname=StringField('First Name',[validators.Length(min=1,max=50)])
    lname = StringField('Last Name', [validators.Length(min=1, max=50)])
    email=StringField('Email',[validators.Length(min=6,max=50)])
    password=PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm',message='Password do not Match')
    ])
    confirm=PasswordField('confirm password')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized Please login','danger')
            return redirect(url_for('login'))
    return wrap

from datetime import datetime, timedelta

@app.route('/',methods = ['POST', 'GET'])
def index():
    # loggedIn,email = getLoginDetails()
    # download = request.args.get('download', None)
    # cur = mysql.connection.cursor()
    # today = datetime.now()
    # past_90_date = today + timedelta(days=-90)
    # print(past_90_date)
    # abc='''SELECT transitions.Name,transitions.Emailid,transitions.Phonenumber,transitions.oldcompany,transitions.oldprofile,transitions.oldctc,transitions.oldstipend,transitions.status,transitions.offered_date,newcompany.CompanyName,newcompany.Profile,newcompany.CTC,newcompany.Stipend FROM `transitions`JOIN newcompany ON transitions.Emailid=newcompany.Emailid WHERE offered_date >= "{past_90_date}" '''.format(past_90_date=past_90_date.strftime("%Y-%m-%d"))
    # print('abc-->',abc)
    # cur.execute(abc)
    # print(cur)
    # data=cur.fetchall()
    # print(data)
    # cur.close()
    # curdebar = mysql.connection.cursor()
    # curdebar.execute('''SELECT debar.Name,debar.Emailid,debar.Phonenumber,debar.cohort,debar.debar_startdate,debar.debar_enddate,debar.reason FROM `debar` JOIN newcompany ON debar.Emailid=newcompany.Emailid''')
    # data_debar=curdebar.fetchall()
    # return render_template('index.html',loggedIn=loggedIn,data=data,data_debar=data_debar)
    return render_template('index.html')

@app.route('/download', methods=['GET', 'POST'])
def download_file():
    p="transitiondebar.xlsx"
    return send_file(p,as_attachment=True)

@app.route('/downloaddrive', methods=['GET', 'POST'])
def download_filedrive():
    p="Drivestatus.xlsx"
    return send_file(p,as_attachment=True)

@app.route('/drivestatus')
def drivestatus():
    return render_template('drivestatus.html')

UPLOAD_FOLDER = '../transitionproject/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload',methods = ['POST', 'GET'])
def upload():
    template_messages = []
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        file = request.files['upload_file']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        data=pd.read_excel(file, engine='openpyxl', usecols=['Name','Email id','Phone number','Company Name','Profile','CTC','Stipend'])
        json_data = json.loads(data.to_json(orient='records'))
        print('json_data-->',json_data)
        for record in json_data:
            Name = record['Name']
            email = record['Email id']
            Phone = record['Phone number']
            CompanyName = record['Company Name']
            Profile = record['Profile']
            CTC = record['CTC']
            Stipend = record['Stipend']
            final_sql = "INSERT INTO newcompany (Name,Emailid,Phonenumber,CompanyName,Profile,CTC,Stipend) VALUES ('{Name}','{Emailid}', {Phonenumber},'{CompanyName}','{Profile}','{CTC}','{Stipend}')".format(
                Name=Name, Emailid=email, Phonenumber=Phone, CompanyName=CompanyName, Profile=Profile, CTC=CTC,
                Stipend=Stipend)
            cur.execute(final_sql)
            print('final_sql--->', final_sql)
        mysql.connection.commit()
        final_drives=[]
        total_file_count = len(json_data)
        matched_records_count = 0
        matched_records_count_debar = 0
        today = datetime.now()
        past_90_date = today + timedelta(days=-90)
        print(past_90_date)
        a_key = "Email id"
        email_checked_data =[a_dict[a_key] for a_dict in json_data]
        print('values_of_key',email_checked_data)
        cur_file = mysql.connection.cursor()
        if len(email_checked_data) == 1:
            email_checked_datas = f"('{email_checked_data[0]}')"
        else:
            email_checked_datas= tuple(email_checked_data)
        print(email_checked_datas, '\n\n')
        sql_query = '''SELECT DISTINCT transitions.Name,transitions.Emailid,transitions.Phonenumber,transitions.oldcompany,transitions.oldprofile,transitions.oldctc,transitions.oldstipend,transitions.status,transitions.offered_date ,newcompany.CompanyName,newcompany.Profile,newcompany.CTC,newcompany.Stipend FROM transitions JOIN newcompany ON transitions.Emailid=newcompany.Emailid  WHERE offered_date  BETWEEN "{past_90_date}" AND "{today}" AND transitions.Emailid IN {email_checked_datas}'''.format(
            email_checked_datas=email_checked_datas,past_90_date=past_90_date.date(),today=today.date())
        print('abc-->', sql_query)
        cur_file.execute(sql_query)
        abcde= cur_file.fetchall()
        print('abcde-->', abcde)
        curdebar = mysql.connection.cursor()
        sql_query_debarr = '''SELECT debar.Name,debar.Emailid,debar.Phonenumber,debar.cohort,debar.debar_startdate,debar.debar_enddate,debar.reason FROM `debar` WHERE debar.Emailid IN {email_checked_datas}'''.format(
            email_checked_datas=email_checked_datas, past_90_date=past_90_date, today=today)
        print('sql_query_debarr-->', sql_query_debarr)
        curdebar.execute(sql_query_debarr)
        data_debar = curdebar.fetchall()
        print('data_debar-->', data_debar)
        new_data = []
        if abcde:
            for row in abcde:
                new_data.append(row)
        new_datas = new_data
        matched_records_count += len(new_data)
        print('total_file_count-->', total_file_count)
        print('matched_records_count-->', matched_records_count)
        print('new_datas-->', new_datas)
        new_data_debar=[]
        if data_debar:
            for rows in data_debar:
                new_data_debar.append(rows)
        new_datas_debar = new_data_debar
        matched_records_count_debar += len(new_data_debar)
        print('total_file_count-->', total_file_count)
        print('matched_records_count-->', matched_records_count_debar)
        print('new_datas_debar-->', new_datas_debar)
        return render_template('index.html',new_datas_debar=new_datas_debar,matched_records_count_debar=matched_records_count_debar,new_datas=new_datas,total_file_count=total_file_count,matched_records_count=matched_records_count)
    return redirect(url_for('index',template_messages=template_messages))


@app.route('/uploadtransition', methods=['GET', 'POST'])
def uploadadmin():
        if request.method == 'POST':
            template_messages=[]
            file = request.files['upload_file']
            data=pd.read_excel(file, engine='openpyxl', usecols=['Name', 'Phonenumber',
                'Emailid', 'oldcompany', 'oldprofile', 'oldctc','oldstipend','status','offered_date'])
            json_data = json.loads(data.to_json(orient='records'))
            final_drives = []
            cur = mysql.connection.cursor()
            for record in json_data:
                Name = record['Name']
                Phonenumber = record['Phonenumber']
                Emailid = record['Emailid']
                oldcompany = record['oldcompany']
                oldprofile=record['oldprofile']
                oldctc = record['oldctc']
                oldstipend = record['oldstipend']
                status = record['status']
                offered_date=record['offered_date']
                print(f"{type(offered_date)}------------> ", offered_date)
                if offered_date and type(offered_date) == int:
                    offered_date = datetime.fromtimestamp(offered_date)
                if Emailid:
                    final_sql = "INSERT INTO transitions (Name,Phonenumber,Emailid,oldcompany,oldprofile,oldctc,oldstipend,status,offered_date) VALUES ('{Name}','{Phonenumber}','{Emailid}','{oldcompany}','{oldprofile}','{oldctc}','{oldstipend}','{status}','{offered_date}')".format(Name=Name,Phonenumber=Phonenumber,Emailid=Emailid,oldcompany=oldcompany,oldprofile=oldprofile,oldctc=oldctc,oldstipend=oldstipend,status=status,offered_date=offered_date)
                    print('final_sql--->',final_sql)
                else:
                    pass
                cur.execute(final_sql)
                mysql.connection.commit()
                final_drives.append('1')
            cur.close()
            temp_msg = {
                "msg_type": 1,
                "msg": "Transitions data is inserted successfully "
            }
            template_messages.append(temp_msg)
            flash(u'Transitions data is inserted successfully ', 'success')
            return redirect(url_for('admin',data=final_drives,template_messages=template_messages))
        return render_template('admin.html')


@app.route('/bulkstatus',methods = ['POST', 'GET'])
def bulkstatus():
    template_messages = []
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        file = request.files['upload_file']
        print(f'sendemail --> {sendemail}')
        data = pd.read_excel(file, engine='openpyxl', usecols=['Learner Name','Email Address','Company Name', 'Profile', 'Drive status', 'Status'])
        json_data = json.loads(data.to_json(orient='records'))
        final_drives = []
        cur = mysql.connection.cursor()
        print('json_data--->', json_data)
        x={}
        for row in json_data:
            if row['Email Address'] in x:
                x[row['Email Address']].append([row['Learner Name'],row['Company Name'],row['Profile'],row['Drive status'],row['Status']])
            else:
                x[row['Email Address']] = [[row['Learner Name'],row['Company Name'],row['Profile'],row['Drive status'],row['Status']]]
        print('x---->',x)
        index = 0
        for key, value in x.items():
            if value:
                print('value--->',value)

                name = value[0][0]

                print(f'{index} -- {key} ------> {value}')
                index+=1
                msg = Message("Company Round Wise Status",
                              sender="drives@upgrad.com",
                              recipients=[key])
                msg.html = render_template('mailtemplate.html', name=name, data=value)
                mail.send(msg)
                print(f"Mail --> {index}")
        temp_msg = {
            "msg_type": 1,
            "msg": "Successfully send mail to " + key
        }
        template_messages.append(temp_msg)
        flash(u'Mail has been sent', 'success')
        for record in json_data:
            Learnername = record['Learner Name']
            email_id = record['Email Address']
            CompanyName = record['Company Name']
            Profile = record['Profile']
            Drive_status = record['Drive status']
            status = record['Status']
            final_sql = "INSERT INTO drivestatus (Learnername,email_id,CompanyName,Profile,Drive_status,status) VALUES " \
                        "('{Learnername}','{email_id}','{CompanyName}','{Profile}','{Drive_status}','{status}')".format(
                Learnername=Learnername, email_id=email_id, CompanyName=CompanyName, Profile=Profile,
                Drive_status=Drive_status,
                status=status)
            cur.execute(final_sql)
            print('final_sql--->', final_sql)
        mysql.connection.commit()
        return render_template('drivestatus.html',template_messages=template_messages)
    return render_template('drivestatus.html',template_messages=template_messages)


@app.route('/admin',methods=['GET','POST'])
def admin():
    try:
        loggedIn, email = getLoginDetails()
        return render_template('admin.html',loggedIn=loggedIn, email=email)
    except Exception as e:
        print("Admin Exception -------------> ", e)
        return render_template('admin.html')



@app.route('/sendemail/<string:studid>', methods = ['GET'])
def sendemail(studid):
    email = session['email']
    mail.send_message("New Message from Admin," + "Details Are: Thanks for Registering",sender=['meghawadhwa138@gmail.com'],
                      recipients=['email'],
                      body='This mail is for testing Purposes only...' + 'your id is :' + studid)
    return redirect(url_for('admin'))


@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method=="POST":
        email = request.form['email']
        password_candidate=request.form['password']
        cur=mysql.connection.cursor()
        result=cur.execute('''SELECT * FROM user WHERE email=%s''',[email])
        if result>0:
            data=cur.fetchone()
            password=data[4]
            if password:
                session['logged_in']=True
                session['email']=email
                flash('You are now logged in','success')
                return redirect('admin.html')
            else:
                error='Invalid email or password'
                return render_template('login.html',error=error)

        else:
            flash('Username Not Found ','fail')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisteredForm(request.form)
    if request.method == 'POST' and form.validate():
        fname = form.fname.data
        lname = form.lname.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO user(fname,lname,email,password) VALUES(%s,%s,%s,%s)''',
                    (fname,lname,email,password))
        mysql.connection.commit()
        cur.close()
        flash('You are now registered and can login now', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('admin'))

@app.route("/learners",methods=['GET','POST'])
def learners():
    if request.method=="POST":
        cur = mysql.connection.cursor()
        cur.execute(
            '''SELECT DISTINCT programname FROM learners_data''')
        programlist = cur.fetchall()
        cur_skills = mysql.connection.cursor()
        cur_skills.execute(
            '''SELECT DISTINCT LOWER(skills) FROM learners_data  GROUP BY(skills) HAVING COUNT(skills)=1 ORDER BY skills ASC''')
        skillslist = cur_skills.fetchall()
        final_skills_list = []
        for record in skillslist:
            temp = record[0].split(',')
            final_skills_list += temp
        final_skills_list = list(map(lambda skill: str(skill).replace("\n", '').strip(), final_skills_list))
        final_skills_list = tuple(set(final_skills_list))
        print(final_skills_list)
        final_skills_list = tuple(set(final_skills_list))
        print('skillslist---->', skillslist)
        print('final_skills_listele---->', final_skills_list[0])
        return render_template('learners.html',final_skills_list=final_skills_list,programlist=programlist)
    return render_template('learners.html')

@app.route('/entiredatatransition/',methods=['GET','POST'])
def entiredatatransition():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT DISTINCT Name,Phonenumber,Emailid,oldcompany,oldprofile,oldctc,oldstipend,status,offered_date FROM transitions''')
    data=cur.fetchall()
    download = request.args.get('download', None)
    print('data--->',data)
    if download == '1':
        output = io.StringIO()
        writer = csv.writer(output)
        print('transition---->', data)
        line = ['Name', 'Phonenumber', 'Emailid', 'oldcompany', 'oldprofile', 'oldctc',
                'oldstipend', 'status', 'offered_date']
        writer.writerow(line)
        for row in data:
            line = [
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]
            writer.writerow(line)
        output.seek(0)
        return Response(output, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=transitions.csv"})
    return redirect(url_for('index'))

@app.route('/entiredatadebar/',methods=['GET','POST'])
def entiredatadebar():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT DISTINCT Name,Emailid,Phonenumber,cohort,debar_startdate,debar_enddate,reason FROM debar''')
    datadebar=cur.fetchall()
    download = request.args.get('download', None)
    print('data--->',datadebar)
    if download == '1':
        output = io.StringIO()
        writer = csv.writer(output)
        print('datadebar---->', datadebar)
        line = ['Name', 'Emailid', 'Phonenumber', 'cohort', 'debar_startdate', 'debar_enddate',
                'reason']
        writer.writerow(line)
        for row in datadebar:
            line = [
                row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
            writer.writerow(line)
        output.seek(0)
        return Response(output, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=debarred_learners.csv"})
    return redirect(url_for('index'))

@app.route("/download/report/excel",methods=['GET','POST'])
def download():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT DISTINCT Name,Phonenumber,Emailid,oldcompany,oldprofile,oldctc,oldstipend,status,offered_date FROM transitions''')
    result=cur.fetchall()
    output=io.BytesIO()
    workbook=xlwt.Workbook()
    sh=workbook.add_sheet("transitions")
    sh.write(0,0,'Name')
    sh.write(0,1,'Phonenumber')
    sh.write(0, 2, 'Emailid')
    sh.write(0, 3, 'oldcompany')
    sh.write(0, 4, 'oldprofile')
    sh.write(0, 5, 'oldctc')
    sh.write(0, 6, 'oldstipend')
    sh.write(0, 7, 'status')
    sh.write(0, 8, 'offered_date')
    idx=0
    for row in result:
        sh.write(idx+1,0,row[0])
        sh.write(idx + 1, 1, row[1])
        sh.write(idx + 1, 2, row[2])
        sh.write(idx + 1, 3, row[3])
        sh.write(idx + 1, 4, row[4])
        sh.write(idx + 1, 5, row[5])
        sh.write(idx + 1, 6, row[6])
        sh.write(idx + 1, 7, row[7])
        sh.write(idx + 1, 8, row[8])
        idx+=1
        workbook.save(output)
        output.seek(0)
        return Response(output,mimetype="application/ms-excel",headers={"Content-Disposition":"attachment;filename=transitions.xlsx"})


@app.route('/learnersfilter', methods=['GET', 'POST'])
def learnersfilter():
    cur = mysql.connection.cursor()
    cur.execute(
        '''SELECT DISTINCT programname FROM learners_data''')
    programlist = cur.fetchall()
    cur_skills = mysql.connection.cursor()
    cur_skills.execute(
        '''SELECT DISTINCT LOWER(skills) FROM learners_data  GROUP BY(skills) HAVING COUNT(skills)=1 ORDER BY skills ASC''')
    skillslist = cur_skills.fetchall()
    final_skills_list = []
    for record in skillslist:
        temp = record[0].split(',')
        final_skills_list += temp
    final_skills_list = list(map(lambda skill: str(skill).replace("\n", '').strip(), final_skills_list))
    final_skills_list = tuple(set(final_skills_list))
    print(final_skills_list)
    final_skills_list = tuple(set(final_skills_list))
    print('skillslist---->', skillslist)
    print('final_skills_listele---->', final_skills_list[0])
    download = request.args.get('download', None)
    if request.method == "POST":
        Name = request.form.get('Name', None)
        email_id = request.form.get('email_id', None)
        Gender = request.form.get('Gender', None)
        Current_Organisation = request.form.get('Current_Organisation', None)
        Current_Designation = request.form.get('Current_Designation', None)
        programname = request.form.get('programname', None)
        cohortid = request.form.get('cohortid', None)
        location = request.form.get('location', None)
        Current_CTC_Min = request.form.get('Current_CTC_Min', None)
        Current_CTC_Max = request.form.get('Current_CTC_Max', None)
        skills = request.form.get('skills', None)
        min_exp = request.form.get('min_exp', None)
        max_exp = request.form.get('max_exp', None)
        notice_period = request.form.get('notice_period', None)
        passout_year = request.form.get('passout_year', None)
        looking_for_job = request.form.get('looking_for_job', None)
        cur = mysql.connection.cursor()
        filter_query = []
        form_data = {}
        if Name:
            form_data['Name'] = Name
            filter_query.append(f" Name LIKE '{Name}%' ")
        if email_id:
            form_data['email_id'] = email_id
            filter_query.append(f'email_id LIKE "{email_id}%"')
        if Gender:
            form_data['Gender'] = Gender
            filter_query.append(f'learners_data.Gender LIKE "{Gender}%"')
        if Current_Organisation:
            form_data['Current_Organisation'] = Current_Organisation
            filter_query.append(f'learners_data.Current_Organisation LIKE "{Current_Organisation}%"')
        if Current_Designation:
            form_data['Current_Designation'] = Current_Designation
            filter_query.append(f'learners_data.Current_Designation LIKE  "{Current_Designation}%"')
        if programname:
            form_data['programname'] = programname
            filter_query.append(f'learners_data.programname LIKE  "{programname}%"')
        if cohortid:
            form_data['cohortid'] = cohortid
            filter_query.append(f'learners_data.cohortid LIKE  "{cohortid}%"')
        if location:
            form_data['location'] = location
            filter_query.append(f'learners_data.location LIKE  "{location}%"')
        if skills:
            form_data['skills'] = skills
            print('skills--->', skills)
            print(form_data)
            filter_query.append(f'learners_data.skills LIKE  "{skills}%"')
        if notice_period:
            form_data['notice_period'] = notice_period
            filter_query.append(f'learners_data.notice_period LIKE  "{notice_period}%"')
        if passout_year:
            form_data['passout_year'] = passout_year
            filter_query.append(f'learners_data.passout_year LIKE  "{passout_year}%"')
        if looking_for_job:
            form_data['looking_for_job'] = looking_for_job
            filter_query.append(f'learners_data.looking_for_job LIKE  "{looking_for_job}%"')
        if Current_CTC_Min:
            form_data['Current_CTC_Min'] = Current_CTC_Min
            # filter_query.append(f'learners_data.Current_CTC >= {Current_CTC_Min}')
            try:
                Current_CTC_Min = int(Current_CTC_Min)
                filter_query.append(f'learners_data.Current_CTC >= {Current_CTC_Min}')
            except:
                pass
        if Current_CTC_Max:
            form_data['Current_CTC_Max'] = Current_CTC_Max
            try:
                Current_CTC_Max = int(Current_CTC_Max)
                filter_query.append(f'learners_data.Current_CTC <= {Current_CTC_Max}')
            except:
                pass
        '''

        # 1. Frontend - javascript - DropDown Listener
        2. form data
        3. query_filter
        4. col contains "%{form_data_value}%"
        5. Select * from .... + query_filrter
        '''

        '''

        '''
        if min_exp:
            form_data['min_exp'] = min_exp
            try:
                min_exp = int(min_exp)
                filter_query.append(f'learners_data.work_exp >= {min_exp}')
            except:
                pass
        if max_exp:
            form_data['max_exp'] = max_exp
            try:
                max_exp = int(max_exp)
                filter_query.append(f'learners_data.work_exp <= {max_exp}')
            except:
                pass
        final_filter_query = None
        if filter_query:
            if len(filter_query) > 1:
                final_filter_query = ' AND '.join(filter_query)
            else:
                final_filter_query = filter_query[0]
        final_filter_query = None
        if filter_query:
            final_filter_query = ' AND '.join(filter_query)
        sql_query = f'SELECT learner_id, Name,email_id,Phonenumber, Gender,Current_Organisation,Current_Designation,location,internship,Current_CTC,work_exp,notice_period,skills,Degree,passout_year,resume,programname,cohortid,looking_for_job FROM learners_data' + (
            f' WHERE {final_filter_query}' if final_filter_query else '')
        print('sql_query', sql_query)
        cur.execute(sql_query)
        mysql.connection.commit()
        student = cur.fetchall()
        print(student)
        cur.close()
        return render_template('learners.html', form_data=form_data,
                               final_filter_query=final_filter_query, student=student,
                               final_skills_list=final_skills_list, programlist=programlist)

    elif request.method == "GET":
        if download == '1':
            Name = request.args.get('Name', None)
            print(" -- >", Name)
            email_id = request.form.get('email_id ', None)
            Gender = request.form.get('Gender', None)
            Current_Organisation = request.form.get('Current_Organisation', None)
            Current_Designation = request.form.get('Current_Designation', None)
            programname = request.form.get('programname', None)
            cohortid = request.form.get('cohortid', None)
            location = request.form.get('location', None)
            Current_CTC_Min = request.form.get('Current_CTC_Min ', None)
            Current_CTC_Max = request.form.get('Current_CTC_Max', None)
            skills = request.form.get('skills', None)
            min_exp = request.form.get('min_exp', None)
            max_exp = request.form.get('max_exp', None)
            notice_period = request.form.get('notice_period', None)
            passout_year = request.form.get('passout_year', None)
            looking_for_job = request.form.get('looking_for_job', None)
            cur = mysql.connection.cursor()
            filter_query = []
            form_data = {}
            company_query = []
            student_query = []
            if Name:
                form_data['Name'] = Name
                filter_query.append(f'lower(Name) LIKE "{Name}%"')
            if email_id:
                form_data['email_id'] = email_id
                filter_query.append(f'email_id LIKE "{email_id}%"')
            if Gender:
                form_data['Gender'] = Gender
                filter_query.append(f'Gender LIKE "{Gender}%"')
            if Current_Organisation:
                form_data['Current_Organisation'] = Current_Organisation
                filter_query.append(f'Current_Organisation LIKE "{Current_Organisation}%"')
            if Current_Designation:
                form_data['Current_Designation'] = Current_Designation
                filter_query.append(f'Current_Designation LIKE  "{Current_Designation}%"')
            if programname:
                form_data['programname'] = programname
                filter_query.append(f'programname LIKE  "{programname}%"')
            if cohortid:
                form_data['cohortid'] = cohortid
                filter_query.append(f'cohortid LIKE  "{cohortid}%"')
            if Current_CTC_Min:
                form_data['Current_CTC_Min'] = Current_CTC_Min
                filter_query.append(f'Current_CTC_Min LIKE  "{Current_CTC_Min}%"')
            if Current_CTC_Max:
                form_data['Current_CTC_Max'] = Current_CTC_Max
                filter_query.append(f'Current_CTC_Max LIKE  "{Current_CTC_Max}%"')
            if skills:
                form_data['skills'] = skills
                filter_query.append(f'skills LIKE  "{skills}%"')
            if min_exp:
                form_data['min_exp'] = min_exp
                filter_query.append(f'min_exp LIKE  "{min_exp}%"')
            if max_exp:
                form_data['max_exp'] = max_exp
                filter_query.append(f'max_exp LIKE  "{max_exp}%"')
            if notice_period:
                form_data['notice_period'] = notice_period
                filter_query.append(f'notice_period LIKE  "{notice_period}%"')
            if passout_year:
                form_data['passout_year'] = passout_year
                filter_query.append(f'passout_year LIKE  "{passout_year}%"')
            if looking_for_job:
                form_data['looking_for_job'] = looking_for_job
                filter_query.append(f'looking_for_job LIKE  "{looking_for_job}%"')
            final_filter_query = None
            if filter_query:
                if len(filter_query) > 1:
                    final_filter_query = ' AND '.join(filter_query)
                else:
                    final_filter_query = filter_query[0]

            final_filter_query = None
            print(final_filter_query)
            if filter_query:
                final_filter_query = ' AND '.join(filter_query)
            sql_query = f'SELECT Name,email_id,Phonenumber, Gender,Current_Organisation,Current_Designation,location,internship,Current_CTC,work_exp,notice_period,skills,Degree,passout_year,resume,programname,cohortid,looking_for_job FROM learners_data' + (
                f' WHERE {final_filter_query}' if final_filter_query else '')
            cur.execute(sql_query)
            mysql.connection.commit()
            student = cur.fetchall()
            print('data coming--->', student)
            cur.close()
            output = io.StringIO()
            writer = csv.writer(output)
            #
            # print('student---->',student)
            #
            # print(type(student))

            line = ['Name', 'email_id', 'Phonenumber', 'Gender', 'Current_Organisation', 'Current_Designation',
                    'location', 'internship', 'Current_CTC', 'work_exp', 'notice_period', 'skills', 'Degree',
                    'passout_year',
                    'resume', '	programname', 'cohortid', '	looking_for_job', ]
            writer.writerow(line)

            for row in student:
                # print(f'line ==> {type(row)}')
                # print(f'line ==> {row}')
                line = [
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14], row[15], row[16], row[17]]
                writer.writerow(line)
            output.seek(0)
            return Response(output, mimetype="text/csv",
                            headers={"Content-Disposition": "attachment;filename=Drive Registrations.csv"})
    return render_template('learners.html', final_skills_list=final_skills_list, programlist=programlist)


@app.route('/learnerwithfilters',methods=['GET', 'POST'])
def learnerwithfilters():
    cur = mysql.connection.cursor()
    cur.execute(
        '''SELECT DISTINCT programname FROM learners_data''')
    programlist = cur.fetchall()
    cur_skills = mysql.connection.cursor()
    cur_skills.execute(
        '''SELECT DISTINCT LOWER(skills) FROM learners_data  GROUP BY(skills) HAVING COUNT(skills)=1 ORDER BY skills ASC''')
    skillslist = cur_skills.fetchall()
    final_skills_list = []
    for record in skillslist:
        temp = record[0].split(',')
        final_skills_list += temp
    final_skills_list = list(map(lambda skill: str(skill).replace("\n", '').strip(), final_skills_list))
    final_skills_list = tuple(set(final_skills_list))
    print(final_skills_list)
    final_skills_list = tuple(set(final_skills_list))
    print('skillslist---->', skillslist)
    print('final_skills_listele---->', final_skills_list[0])
    download = request.args.get('download', None)
    if request.method == "POST":
        print("From Args", request.args)
        print("From Data", request.data)
        print("From Data", request.form)
        Name = request.form.get('Name', None)
        email_id = request.form.get('email_id', None)
        Gender = request.form.get('Gender', None)
        Current_Organisation = request.form.get('Current_Organisation', None)
        Current_Designation = request.form.get('Current_Designation', None)
        programname = request.form.get('programname', None)
        cohortid = request.form.get('cohortid', None)
        location = request.form.get('location', None)
        Current_CTC_Min = request.form.get('Current_CTC_Min', None)
        Current_CTC_Max = request.form.get('Current_CTC_Max', None)
        skills = request.form.get('skills', None)
        min_exp= request.form.get('min_exp', None)
        max_exp= request.form.get('max_exp', None)
        notice_period= request.form.get('notice_period', None)
        passout_year= request.form.get('passout_year', None)
        looking_for_job= request.form.get('looking_for_job', None)
        domain= request.form.get('domain', None)
        cur = mysql.connection.cursor()
        filter_query = []
        form_data = {}
        if Name:
            form_data['Name'] = Name
            filter_query.append(f" Name LIKE '{Name}%' ")
        if email_id:
            form_data['email_id'] = email_id
            filter_query.append(f'email_id LIKE "{email_id}%"')
        if Gender:
            form_data['Gender'] = Gender
            filter_query.append(f'learners_data.Gender LIKE "{Gender}%"')
        if Current_Organisation:
            form_data['Current_Organisation'] = Current_Organisation
            filter_query.append(f'learners_data.Current_Organisation LIKE "{Current_Organisation}%"')
        if Current_Designation:
            form_data['Current_Designation'] = Current_Designation
            filter_query.append(f'learners_data.Current_Designation LIKE  "{Current_Designation}%"')
        if programname:
            form_data['programname'] = programname
            filter_query.append(f'learners_data.programname LIKE  "{programname}%"')
        if cohortid:
            form_data['cohortid'] = cohortid
            filter_query.append(f'learners_data.cohortid LIKE  "{cohortid}%"')
        if location:
            form_data['location'] = location
            filter_query.append(f'learners_data.location LIKE  "{location}%"')
        if skills:
            form_data['skills'] = skills
            print('skills--->',skills)
            print(form_data)
            filter_query.append(f'learners_data.skills LIKE  "{skills}%"')
        if notice_period:
            form_data['notice_period'] = notice_period
            filter_query.append(f'learners_data.notice_period LIKE  "{notice_period}%"')
        if passout_year:
            form_data['passout_year'] = passout_year
            filter_query.append(f'learners_data.passout_year LIKE  "{passout_year}%"')
        if looking_for_job:
            form_data['looking_for_job'] = looking_for_job
            filter_query.append(f'learners_data.looking_for_job LIKE  "{looking_for_job}%"')
        if domain:
            form_data['domain'] = domain
            filter_query.append(f'learners_data.domain = {domain}')
        if Current_CTC_Min:
            form_data['Current_CTC_Min'] = Current_CTC_Min
            #filter_query.append(f'learners_data.Current_CTC >= {Current_CTC_Min}')
            try:
                Current_CTC_Min = int(Current_CTC_Min)
                filter_query.append(f'learners_data.Current_CTC >= {Current_CTC_Min}')
            except:
                pass
        if Current_CTC_Max:
            form_data['Current_CTC_Max'] = Current_CTC_Max
            try:
                Current_CTC_Max = int(Current_CTC_Max)
                filter_query.append(f'learners_data.Current_CTC <= {Current_CTC_Max}')
            except:
                pass
        '''
        
        # 1. Frontend - javascript - DropDown Listener
        2. form data
        3. query_filter
        4. col contains "%{form_data_value}%"
        5. Select * from .... + query_filrter
        '''

        '''
        
        '''
        if min_exp:
            form_data['min_exp'] = min_exp
            try:
                min_exp = int(min_exp)
                filter_query.append(f'learners_data.work_exp >= {min_exp}')
            except:
                pass
        if max_exp:
            form_data['max_exp'] = max_exp
            try:
                max_exp = int(max_exp)
                filter_query.append(f'learners_data.work_exp <= {max_exp}')
            except:
                pass
        final_filter_query = None
        if filter_query:
            if len(filter_query) > 1:
                final_filter_query = ' AND '.join(filter_query)
            else:
                final_filter_query = filter_query[0]
        final_filter_query = None
        if filter_query:
            final_filter_query = ' AND '.join(filter_query)
        Python = request.form.get("python", None)
        Java = request.form.get("java", None)
        React = request.form.get("react", None)
        Nodejs = request.form.get("node", None)
        DSA = request.form.get("dsa", None)
        Cloud = request.form.get("cloud", None)
        Javascript = request.form.get("js", None)
        Database_know = request.form.get("dbsql", None)
        excel = request.form.get("excel", None)
        etl = request.form.get("etl", None)
        hadoop = request.form.get("hadoop", None)
        nlp = request.form.get("nlp", None)
        datawarehouse = request.form.get("datawarehouse", None)


        #DS------------------------------------------------------------------------------------

        if excel or etl or hadoop or nlp or datawarehouse:
            ds_filters = []
            final_ds_query = None
            if excel:
                ds_filters.append(f'learners_data_ds.excel = {excel}')
            if etl:
                ds_filters.append(f'learners_data_ds.etl = {etl}')
            if hadoop:
                ds_filters.append(f'learners_data_ds.hadoop = {hadoop}')
            if nlp:
                ds_filters.append(f'learners_data_ds.nlp = {nlp}')
            if datawarehouse:
                ds_filters.append(f'learners_data_ds.datawarehouse = {datawarehouse}')

            if ds_filters:
                final_ds_query = ' AND '.join(ds_filters)

            sql_query = f'SELECT learners_data.learner_id, learners_data.Name,learners_data.email_id,learners_data.Phonenumber, learners_data.Gender,learners_data.Current_Organisation,learners_data.Current_Designation,learners_data.location,learners_data.internship,learners_data.Current_CTC,learners_data.work_exp,learners_data.notice_period,learners_data.skills,learners_data.Degree,learners_data.passout_year,learners_data.resume,learners_data.programname,learners_data.cohortid,learners_data.looking_for_job,learners_data.domain FROM learners_data JOIN final_ds_query ON final_ds_query.learner_id=learners_data.learner_id ' + (
                " AND " + final_ds_query if final_ds_query else '') + (
                            f' WHERE {final_filter_query}' if final_filter_query else '')


#SD-----------------------------------------------------------
        if Python or Java or React or Nodejs or DSA or Cloud or Javascript or Database_know:
            sd_filters = []
            final_sd_query=None
            if Python:
                sd_filters.append(f'learners_data_sd.Python = {Python}')
            if Java:
                sd_filters.append(f'learners_data_sd.Java = {Java}')
            if React:
                sd_filters.append(f'learners_data_sd.React = {React}')
            if Nodejs:
                sd_filters.append(f'learners_data_sd.Nodejs = {Nodejs}')
            if DSA:
                sd_filters.append(f'learners_data_sd.DSA = {DSA}')
            if Cloud:
                sd_filters.append(f'learners_data_sd.Cloud = {Cloud}')
            if Javascript:
                sd_filters.append(f'learners_data_sd.Javascript = {Javascript}')
            if Database_know:
                sd_filters.append(f'learners_data_sd.Database_know = {Database_know}')
            if sd_filters:
                final_sd_query = ' AND '.join(sd_filters)

            sql_query = f'SELECT learners_data.learner_id, learners_data.Name,learners_data.email_id,learners_data.Phonenumber, learners_data.Gender,learners_data.Current_Organisation,learners_data.Current_Designation,learners_data.location,learners_data.internship,learners_data.Current_CTC,learners_data.work_exp,learners_data.notice_period,learners_data.skills,learners_data.Degree,learners_data.passout_year,learners_data.resume,learners_data.programname,learners_data.cohortid,learners_data.looking_for_job,learners_data.domain FROM learners_data JOIN learners_data_sd ON learners_data_sd.learner_id=learners_data.learner_id ' + (" AND " + final_sd_query if final_sd_query else '') + (f' WHERE {final_filter_query}' if final_filter_query else '')

        else:
            sql_query = f'SELECT learner_id, Name,email_id,Phonenumber, Gender,Current_Organisation,Current_Designation,location,internship,Current_CTC,work_exp,notice_period,skills,Degree,passout_year,resume,programname,cohortid,looking_for_job,domain FROM learners_data' + (f' WHERE {final_filter_query}' if final_filter_query else '')
        print('sql_query',sql_query)
        cur.execute(sql_query)
        mysql.connection.commit()
        student = cur.fetchall()
        print(student)
        cur.close()
        from flask import jsonify
        return jsonify({"student":student, 'table_response': render_template('table_with_model.html', student=student)})
        return render_template('learners.html',form_data=form_data,
                               final_filter_query=final_filter_query,student=student,final_skills_list=final_skills_list,programlist=programlist)
    elif request.method == "GET":
        if download == '1':
            Name  = request.args.get('Name', None)
            print(" -- >", Name)
            email_id  = request.form.get('email_id ', None)
            Gender  = request.form.get('Gender', None)
            Current_Organisation  = request.form.get('Current_Organisation', None)
            Current_Designation  = request.form.get('Current_Designation', None)
            programname  = request.form.get('programname', None)
            cohortid  = request.form.get('cohortid', None)
            location  = request.form.get('location', None)
            Current_CTC_Min   = request.form.get('Current_CTC_Min ', None)
            Current_CTC_Max   = request.form.get('Current_CTC_Max', None)
            skills  = request.form.get('skills', None)
            min_exp=   request.form.get('min_exp', None)
            max_exp  = request.form.get('max_exp', None)
            notice_period  = request.form.get('notice_period', None)
            passout_year  = request.form.get('passout_year', None)
            looking_for_job  = request.form.get('looking_for_job', None)
            cur = mysql.connection.cursor()
            filter_query = []
            form_data = {}
            company_query = []
            student_query = []
            if Name:
                form_data['Name'] = Name
                filter_query.append(f'lower(Name) LIKE "{Name}%"')
            if email_id:
                form_data['email_id'] = email_id
                filter_query.append(f'email_id LIKE "{email_id}%"')
            if Gender:
                form_data['Gender'] = Gender
                filter_query.append(f'Gender LIKE "{Gender}%"')
            if Current_Organisation:
                form_data['Current_Organisation'] = Current_Organisation
                filter_query.append(f'Current_Organisation LIKE "{Current_Organisation}%"')
            if Current_Designation:
                form_data['Current_Designation'] = Current_Designation
                filter_query.append(f'Current_Designation LIKE  "{Current_Designation}%"')
            if programname:
                form_data['programname'] = programname
                filter_query.append(f'programname LIKE  "{programname}%"')
            if cohortid:
                form_data['cohortid'] = cohortid
                filter_query.append(f'cohortid LIKE  "{cohortid}%"')
            if Current_CTC_Min:
                form_data['Current_CTC_Min'] = Current_CTC_Min
                filter_query.append(f'Current_CTC_Min LIKE  "{Current_CTC_Min}%"')
            if Current_CTC_Max:
                form_data['Current_CTC_Max'] = Current_CTC_Max
                filter_query.append(f'Current_CTC_Max LIKE  "{Current_CTC_Max}%"')
            if skills:
                form_data['skills'] = skills
                filter_query.append(f'skills LIKE  "{skills}%"')
            if min_exp:
                form_data['min_exp'] = min_exp
                filter_query.append(f'min_exp LIKE  "{min_exp}%"')
            if max_exp:
                form_data['max_exp'] = max_exp
                filter_query.append(f'max_exp LIKE  "{max_exp}%"')
            if notice_period:
                form_data['notice_period'] = notice_period
                filter_query.append(f'notice_period LIKE  "{notice_period}%"')
            if passout_year:
                form_data['passout_year'] = passout_year
                filter_query.append(f'passout_year LIKE  "{passout_year}%"')
            if looking_for_job:
                form_data['looking_for_job'] = looking_for_job
                filter_query.append(f'looking_for_job LIKE  "{looking_for_job}%"')
            final_filter_query = None
            if filter_query:
                if len(filter_query) > 1:
                    final_filter_query = ' AND '.join(filter_query)
                else:
                    final_filter_query = filter_query[0]

            final_filter_query = None
            print(final_filter_query)
            if filter_query:
                final_filter_query = ' AND '.join(filter_query)
            sql_query = f'SELECT Name,email_id,Phonenumber, Gender,Current_Organisation,Current_Designation,location,internship,Current_CTC,work_exp,notice_period,skills,Degree,passout_year,resume,programname,cohortid,looking_for_job FROM learners_data' + (
                f' WHERE {final_filter_query}' if final_filter_query else '')
            cur.execute(sql_query)
            mysql.connection.commit()
            student = cur.fetchall()
            print('data coming--->', student)
            cur.close()
            output = io.StringIO()
            writer = csv.writer(output)
            #
            # print('student---->',student)
            #
            # print(type(student))

            line = ['Name', 'email_id', 'Phonenumber', 'Gender', 'Current_Organisation', 'Current_Designation',
                    'location', 'internship', 'Current_CTC', 'work_exp', 'notice_period', 'skills', 'Degree',
                    'passout_year',
                    'resume', '	programname', 'cohortid', '	looking_for_job', ]
            writer.writerow(line)

            for row in student:
                # print(f'line ==> {type(row)}')
                # print(f'line ==> {row}')
                line = [
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14], row[15], row[16], row[17]]
                writer.writerow(line)
            output.seek(0)
            return Response(output, mimetype="text/csv",
                            headers={"Content-Disposition": "attachment;filename=Drive Registrations.csv"})
    from flask import jsonify
    context = {
        'final_skills_list': final_skills_list,
        'programlist': programlist,
    }
    return jsonify(context)
    # return render_template('learners.html',final_skills_list=final_skills_list,programlist=programlist)

@app.route('/uploaddebar', methods=['GET', 'POST'])
def uploaddebar():
        if request.method == 'POST':
            template_messages=[]
            file = request.files['upload_file']
            data=pd.read_excel(file, engine='openpyxl', usecols=['Name','Emailid', 'Phonenumber', 'cohort', 'debar_startdate','debar_enddate','reason'])
            json_data = json.loads(data.to_json(orient='records'))
            final_drives = []
            cur = mysql.connection.cursor()
            for record in json_data:
                Name = record['Name']
                Emailid = record['Emailid']
                Phonenumber = record['Phonenumber']
                cohort = record['cohort']
                debar_startdate=record['debar_startdate']
                debar_enddate = record['debar_enddate']
                reason = record['reason']
                if debar_startdate and type(debar_startdate) == int:
                    debar_startdate = datetime.fromtimestamp(debar_startdate)
                if debar_enddate and type(debar_enddate) == int:
                    debar_enddate = datetime.fromtimestamp(debar_enddate)
                if Emailid:
                    final_sql = "INSERT INTO debar (Name,Emailid,Phonenumber,cohort,debar_startdate,debar_enddate,reason) VALUES ('{Name}','{Emailid}','{Phonenumber}','{cohort}','{debar_startdate}','{debar_enddate}','{reason}'".format(Name=Name,Phonenumber=Phonenumber,Emailid=Emailid,debar_startdate=debar_startdate,debar_enddate=debar_enddate,reason=reason,cohort=cohort)
                    print('final_sql--->',final_sql)
                else:
                    pass
                cur.execute(final_sql)
                mysql.connection.commit()
                final_drives.append('1')
            cur.close()
            temp_msg = {
                "msg_type": 1,
                "msg": "Debar data is inserted successfully "
            }
            template_messages.append(temp_msg)
            flash(u'Debar data is inserted successfully ', 'success')
            return redirect(url_for('admin',data=final_drives,template_messages=template_messages))
        return render_template('admin.html')


@app.route('/updatedata', methods=['GET', 'POST'])
def updatedata():
    return render_template('abc.html')



@app.route('/updatelearner', methods=['GET', 'POST'])
def updatelearner():
    if request.method=='POST':
        template_messages =[]
        learner_id= request.form['learner_id']
        print('learner_id--->',learner_id)
        Current_Organisation = request.form['Current_Organisation']
        Current_Designation = request.form['Current_Designation']
        location = request.form['location']
        Current_CTC = request.form['Current_CTC']
        skills = request.form['skills']
        work_exp = request.form['work_exp']
        notice_period = request.form['notice_period']
        resume = request.form['resume']
        looking_for_job = request.form['looking_for_job']
        cur = mysql.connection.cursor()
        check = f'''SELECT learner_id FROM learners_data WHERE learner_id={learner_id}'''

        '''
        # creating processing
        1. fetch data -> form_data
        2. for loop --> insert --> execute --> lerner_id
        3. History Table--> insert with lerner, user_id and fetched_data -- DateTime
        
        
        # update processing
        1. fetch data -> form_data --> bring complete cols
        2. update --> execute --> lerner_id
        3. History Table--> insert with lerner, user_id and fetched_data -- DateTime
        
        
        ## Fetch log
        1. form_data --> learner_id
        2. History Table --> Select * ..... Where learner_id=learner_id (LIMIT 2) (CREATED-DataTime Decending ro) 
        '''
        check1 = cur.execute(check)
        ids = cur.fetchone()
        print("IDS--->", ids)
        debar = 1
        # if ids:
        sql_query = f'''UPDATE learners_data SET Current_Organisation="{Current_Organisation}", Current_Designation="{Current_Designation}",location="{location}",Current_CTC={Current_CTC},skills="{skills}",work_exp={work_exp},notice_period={notice_period},resume="{resume}",looking_for_job="{looking_for_job}" WHERE learner_id={learner_id}'''
        print('sql_query--->', sql_query)
        cur.execute(sql_query)
        mysql.connection.commit()
        temp_msg = {
            "msg_type": 1,
            "msg": "Successfully Saved "
        }
        template_messages.append(temp_msg)
        if template_messages:
            flash(u'Your Changes have been Saved', 'success')
        else:
            flash(u'Your Changes have not been Saved', 'error')
        mysql.connection.commit()
        cur.execute('''SELECT * FROM learners_data''')
        today=datetime.now()
        rows=cur.fetchall()
        for row in rows:
            final_sql = "INSERT INTO student_history (learner_id,Name,email_id,Phonenumber,Gender,Current_Organisation,Current_Designation,location,internship,Current_CTC,work_exp,notice_period,skills,Degree,passout_year,resume,programname,cohortid,looking_for_job,userid,datetime) VALUES ('{Name}','{email_id}', {Phonenumber},'{Gender}','{Current_Organisation}','{Current_Designation}','{location}','{internship}','{Current_CTC}','{work_exp}','{notice_period}','{skills}','{Degree}','{passout_year}','{resume}',{programname}',{cohortid}',{looking_for_job}',{userid}',{datetime}')".format(
               Name=row[1], email_id=row[2], Phonenumber=row[3], Gender=row[4], Current_Organisation=Current_Organisation, Current_Designation=Current_Designation,
                location=location,internship=row[8],Current_CTC=Current_CTC,work_exp=work_exp,notice_period=notice_period,skills=skills,Degree=row[13],passout_year=row[14],resume=resume,programname=row[15],cohortid=row[16],looking_for_job=looking_for_job,userid=row[17],datetime=datetime)
        #cur.execute(final_sql)
        return render_template('learners.html',ids=ids)
    return render_template('learners.html')




