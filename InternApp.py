# from curses import flash
# from flask_wtf.csrf import CSRFProtect, CSRFError
from io import BytesIO
from flask import Flask, render_template, request, session, redirect, flash, jsonify, url_for
from pymysql import connections
import os
import boto3
import botocore
from flask import send_file
# import pdfplumber
# Use BytesIO to handle the binary content
from werkzeug.utils import secure_filename
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompwd,
    db=customdb
)

output = {}
table = 'Student'

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/homepage", methods=['GET', 'POST'])
def homepage():
    return render_template('home.html')

@app.route("/searchStudentPage", methods=['GET', 'POST'])
def searchStudentPage():
    return render_template('comp_searchStudent.html')

@app.route("/coursepage", methods=['GET', 'POST'])
def coursepage():
    return render_template('course.html')

@app.route("/adminHomePage", methods=['GET', 'POST'])
def adminHomePage():
    return render_template('admin_home.html')

@app.route("/compHomePage", methods=['GET', 'POST'])
def compHomePage():
    return render_template('comp_home.html')

@app.route("/studHomePage", methods=['GET', 'POST'])
def studHomePage():
    return render_template('stud_home.html')

@app.route("/studRegisterPage", methods=['GET', 'POST'])
def studRegisterPage():
    return render_template('stud_registerForm.html')

@app.route("/compRegisterPage", methods=['GET', 'POST'])
def compRegisterPage():
    return render_template('comp_companyform.html')

@app.route("/ziyuPortfolio", methods=['GET', 'POST'])
def ziyuPortfolio():
    return render_template('ziyu_portfolio.html')

@app.route("/bingxinPortfolio", methods=['GET', 'POST'])
def bingxinPortfolio():
    return render_template('bingxin_portfolio.html')

@app.route("/justinPortfolio", methods=['GET', 'POST'])
def justinPortfolio():
    return render_template('justin_portfolio.html')

@app.route("/junxianPortfolio", methods=['GET', 'POST'])
def junxianPortfolio():
    return render_template('junxian_portfolio.html')

@app.route("/jianyongPortfolio", methods=['GET', 'POST'])
def jianyongPortfolio():
    return render_template('jianyong_portfolio.html')

@app.route("/xinyiPortfolio", methods=['GET', 'POST'])
def xinyiPortfolio():
    return render_template('xinyi_portfolio.html')

@app.route("/searchStudentProcess", methods=['GET', 'POST'])
def searchStudProcess():
    stud_id = request.form['stud_id']

    search_sql = "SELECT * FROM student WHERE stud_id = %s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, (stud_id))
    rows = cursor.fetchall()

    if rows:
        return render_template('comp_displaySearchStudInfo.html', rows=rows)
    else:
        return "Student does not exist."

    cursor.close()


def authenticate_user(username, password):
    try:
        # Connection is db_conn !!!
        
        cursor = db_conn.cursor()
        cursor.execute("SELECT user_pass, upper(user_role) FROM users WHERE user_id = %s", (username,))
        user_data = cursor.fetchone()
        
        if user_data:
            db_pass, user_role = user_data
            
            # Check if password correct
            if password == db_pass:
                # Redirect users based on their roles
                if user_role == 'ADMIN':
                    return 'adminHomePage' # CHANGE BASED ON IMPLEMENTATION
                elif user_role == 'LECTURER':
                    return 'lecturerViewStudent' # CHANGE BASED ON IMPLEMENTATION
                elif user_role == 'STUDENT':
                    return 'studHomePage' # CHANGE BASED ON IMPLEMENTATION #studHomePage
                elif user_role == 'COMPANY':
                    return 'compHomePage' # CHANGE BASED ON IMPLEMENTATION
                else:
                    return None  # Invalid user_role, access denied
        
        return None  # User not found or passwords don't match, access denied
    
    except Exception as e:
        print("Database error:", str(e))
        return None  # Access denied in case of an error
    
    finally:
        # Close the database connection
        if cursor:
            cursor.close()


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username'] #From index.html
    password = request.form['password'] #From index.html
    
    # Use your authenticate_user function here
    redirect_page = authenticate_user(username, password)
    
    if redirect_page:
        # Store the username in the Flask session
        session['username'] = username
        
        # Redirect to the appropriate page based on user role
        return redirect(url_for(redirect_page))
    else:
        return "Access denied"
    

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))


@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form['signUpUsername'] #From index.html
    password = request.form['signUpPassword'] #From index.html
    roles    = request.form['roles'] #From index.html
    
    insert_sql = "INSERT INTO users VALUES (%s, %s, %s)"
    cursor = db_conn.cursor()
    cursor.execute(insert_sql, (username, password, roles))
    db_conn.commit()
    cursor.close()

    return render_template('index.html')
    

@app.route("/displayStudInfo", methods=['GET', 'POST'])
def viewStudentInfo():
    username = session.get('username')

    if username:
        statement = "SELECT s.* FROM student s JOIN company c ON s.com_email = c.com_email WHERE s.com_email = %s;"

        cursor = db_conn.cursor()
        cursor.execute(statement, (username,))
        result = cursor.fetchall()
        cursor.close()

        return render_template('comp_displayStudInfo.html', data=result)
    
    else:
        return "Nothing found"
    

@app.route('/displayStudInfoDetails/<stud_email>')
def viewStudentInfoDetails(stud_email):
    statement = "SELECT * FROM student s WHERE stud_email = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_email,))
    result = cursor.fetchone()
    
    return render_template('comp_displayStudInfoDet.html', student=result)


@app.route('/displayStudResume/<stud_email>')
def displayStudentResume(stud_email):
    statement = "SELECT stud_email, stud_resume FROM student s WHERE stud_email = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_email,))
    results = cursor.fetchone()
    
    if results: 
        studEmail, resume = results
        resume = "https://" + bucket + ".s3.amazonaws.com/stud-id-" + studEmail + "_pdf.pdf"
        return render_template('comp_displayStudResume.html', results=results, resume=resume)
        
    else: 
        return "Invalid student."
        
    return render_template('comp_displayStudInfoDet.html')
    

# ADDITIONAL FOR LEC_VIEWSTUDENT
@app.route("/lecturerView", methods=['GET', 'POST'])
def lecturerViewStudent():
    username = session.get('username')

    if username:
        statement = "SELECT s.* FROM student s JOIN lecturer l ON l.lec_email = s.lec_email WHERE s.lec_email = %s;"

        cursor = db_conn.cursor()
        cursor.execute(statement, (username,))
        result = cursor.fetchall()
        cursor.close()

        return render_template('lec_viewStudent.html', data=result)
    
    else:
        return "Nothing found"

# ADDITIONAL FOR LEC_VIEWSTUDENT
@app.route('/lecturerViewResume/<stud_email>')
def lecturerViewStudResume(stud_email):
    statement = "SELECT stud_email, stud_resume FROM student s WHERE stud_email = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_email,))
    results = cursor.fetchone()
    
    if results: 
        studEmail, resume = results
        resume_url = "https://" + bucket + ".s3.amazonaws.com/stud-id-" + studEmail + "_pdf.pdf"
        return jsonify({"resume_url": resume_url})
    else: 
        return jsonify({"resume_url": None})

# ADDITIONAL FOR LEC_VIEWSTUDENT
@app.route('/lecturerViewReport/<stud_email>')
def lecturerViewStudReport(stud_email):
    statement = "SELECT stud_email FROM student s WHERE stud_email = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_email,))
    results = cursor.fetchone()
    
    if results: 
        report_url = "https://" + bucket + ".s3.amazonaws.com/stud-id-" + stud_email + "_rpt.pdf"
        return jsonify({"report_url": report_url})
    else: 
        return jsonify({"report_url": None})


@app.route("/displayComInfo", methods=['GET', 'POST'])
def viewCompanyInfo():
    statement = "SELECT com_id,com_name,com_address,com_hp,com_email FROM company WHERE status = 0;"
    cursor = db_conn.cursor()
    cursor.execute(statement)
    result = cursor.fetchall()
    cursor.close()
    return render_template('admin.html', data=result)

@app.route('/delete_company/<com_email>', methods=['POST'])
def delete_company(com_email):
    company_email = request.form.get('com_email')
    statement = "DELETE FROM company WHERE com_email = %s;"
    cursor = db_conn.cursor()
    cursor.execute(statement, (com_email,))
    db_conn.commit()

    # Fetch the updated data from the database
    statement = "SELECT * FROM company WHERE status = 0"
    cursor.execute(statement)
    updated_data = cursor.fetchall()
    cursor.close()

    # Return the updated data as JSON
    return redirect(url_for('viewCompanyInfo'))


@app.route('/update_company_status/<com_email>', methods=['POST'])
def update_company_status(com_email):

        com_email = request.form.get('com_email')
        statement = "UPDATE company SET status = 1 WHERE com_email = %s;"
        cursor = db_conn.cursor()
        cursor.execute(statement, (com_email,))
        db_conn.commit()

        # Fetch the updated data from the database
        statement = "SELECT * FROM company WHERE status = 0"
        cursor.execute(statement)
        updated_data = cursor.fetchall()
        cursor.close()
        return redirect(url_for('viewCompanyInfo'))


# Function to fetch student data for editing
def get_student_data(stud_id):
    cursor = db_conn.cursor()
    cursor.execute(f"SELECT * FROM student WHERE stud_id = {stud_id}")
    student_data = cursor.fetchone()
    cursor.close()
    return student_data



@app.route("/studProfile/", methods=['GET', 'POST'])
def GetStudInfo():
    username = session.get('username')

    if username:
        # Fetch student information from the database
        statement = "SELECT * FROM student WHERE stud_email = %s;"
        cursor = db_conn.cursor()
        cursor.execute(statement, (username,))
        student_data = cursor.fetchone()
        cursor.close()
    
        return render_template('studProfile.html', student=student_data)

    return "Student not found"



# Route to edit student profile
@app.route("/editStudProfile/<stud_email>", methods=['GET', 'POST'])
def EditStudProfile(stud_email):
    username =  session.get('username')
    stud_email = stud_email 

    if username:
        if request.method == 'GET':
            statement = "SELECT * FROM student WHERE stud_email = %s;"
            cursor = db_conn.cursor()
            cursor.execute(statement, (username,))
            student_data = cursor.fetchone()
            cursor.close()
            resume = "https://" + bucket + ".s3.amazonaws.com/stud-id-" + stud_email + "_pdf.pdf"

            #if results: 
                #stud_id, stud_name, stud_gender, stud_IC, stud_email, stud_HP, stud_currAddress, stud_homeAddress, stud_programme, stud_cgpa, stud_resume, stud_cgpa = student_data
                #resume = "https://" + bucket + ".s3.amazonaws.com/stud-id-" + studEmail + "_pdf.pdf"
                #return render_template('comp_displayStudResume.html', student=student_data, resume=resume)
                
            #else: 
                #return "Invalid student."
            
            return render_template('editStudProfile.html', student=student_data)
    

        elif request.method == 'POST':
            # Retrieve form data
            stud_id = request.form['stud_id']
            stud_name = request.form['stud_name']
            stud_programme = request.form['stud_programme']
            # stud_email = request.form['stud_email']
            stud_HP = request.form['stud_HP']
            stud_ic = request.form['stud_ic']
            stud_gender = request.form['stud_gender']
            stud_currAddress = request.form['stud_currAddress']
            stud_homeAddress = request.form['stud_homeAddress']
            stud_image_file = request.files['stud_image_file']

            # Update the database with the new data
            cursor = db_conn.cursor()
            cursor.execute(f"UPDATE student SET stud_id = '{stud_id}',stud_name = '{stud_name}', stud_programme = '{stud_programme}', "
                        f"stud_HP = '{stud_HP}', stud_IC = '{stud_ic}', "
                        f"stud_gender = '{stud_gender}', stud_currAddress = '{stud_currAddress}', "
                        f"stud_homeAddress = '{stud_homeAddress}' WHERE stud_email = {stud_email}")
            db_conn.commit()
            cursor.close()

            # Check if a new resume file is provided
            if stud_resume.filename != "":
                s3 = boto3.resource('s3')
                stud_image_file_name_in_s3 = "stud-id-" + str(stud_email) + "_pdf.pdf"

                try:
                    print("Data inserted in MySQL RDS... updating pdf to S3...")
                    s3.Bucket(custombucket).put_object(Key=stud_image_file_name_in_s3, Body=stud_image_file, ContentType='application/pdf')
                    bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                    s3_location = (bucket_location['LocationConstraint'])

                    if s3_location is None:
                        s3_location = ''
                    else:
                        s3_location = '-' + s3_location

                    object_url = f"https://{custombucket}.s3.amazonaws.com/{stud_image_file_name_in_s3}"

                    # object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    #     s3_location,
                    #     custombucket,
                    #     stud_resume_name_in_s3)
                    
                    # Update the stud_resume field in the database
                    cursor = db_conn.cursor()
                    cursor.execute(f"UPDATE student SET stud_resume = '{object_url}' WHERE stud_email = {stud_email}")
                    db_conn.commit()
                    cursor.close()

                except Exception as e:
                    return str(e)



            flash("Student profile updated successfully", "success")
            return redirect(url_for('GetStudInfo', stud_email=stud_email, object_url=object_url))
    
    return "Student not found"


@app.route("/addemp", methods=['POST'])
def AddEmp():
    stud_id = request.form['stud_id']
    stud_name = request.form['stud_name']
    stud_gender = request.form['stud_gender']
    stud_IC = request.form['stud_ic']
    stud_email = request.form['stud_mail']
    stud_HP = request.form['stud_phone']
    stud_currAddress = request.form['stud_currAddress']
    stud_homeAddress = request.form['stud_homeAddress']
    stud_programme = request.form['stud_program']
    stud_image_file = request.files['stud_image_file']
    stud_pwd = request.form['password']
    stud_cgpa = request.form['stud_cgpa']
    lec_email = request.form['lec_email']
    com_email = request.form['com_email']
    

    insert_sql = "INSERT INTO student VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s ,%s, %s ,%s)"
    cursor = db_conn.cursor()

    if stud_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (stud_id, stud_name, stud_gender, stud_IC, stud_email, stud_HP, stud_currAddress, stud_homeAddress, stud_programme, 
                                    stud_image_file ,stud_pwd, stud_cgpa, lec_email ,com_email))
        db_conn.commit()
        
        # Uplaod image file in S3
        stud_image_file_name_in_s3 = "stud-id-" + str(stud_email) + "_pdf.pdf"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading pdf to S3...")
            s3.Bucket(custombucket).put_object(Key=stud_image_file_name_in_s3, Body=stud_image_file, ContentType='application/pdf')
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = f"https://{custombucket}.s3.amazonaws.com/{stud_image_file_name_in_s3}"

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('stud_addStudOutput.html', name=stud_name, object_url=object_url)
        #return to xinyi


@app.route("/companyform", methods=['GET','POST'])
def companyform():
    if request.method == "POST":

        com_name = request.form['com_name']
        com_address = request.form['com_address']
        com_HP = request.form['com_hp']
        com_email = request.form['com_mail']
        com_description = request.form['com_description']
        com_website = request.form['com_website']
        com_logo_file = request.files['company_logo_file']
        job_title = request.form['job_title']
        job_type = request.form['job_type']
        job_description = request.form['job_description']
    


        insert_sql = "INSERT INTO company VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        if com_logo_file.filename == "":
            return "Please select an image file"

        try:

            cursor.execute(insert_sql, (com_name, com_address, com_HP,com_email,com_description,com_website,job_title,job_type,job_description))
            db_conn.commit()
            # Uplaod image file in S3 #
            comp_image_file_name_in_s3 = str(com_name) + "_logo_image_file"
            s3 = boto3.resource('s3')

            try:
                print("Data inserted in MySQL RDS... uploading image to S3...")
                s3.Bucket(custombucket).put_object(Key=com_image_file_name_in_s3, Body=com_logo_file)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    com_image_file_name_in_s3)

            except Exception as e:
                return str(e)

        finally:
            cursor.close()

        print("all modification done...")
        return render_template('comp_addComOutput.html', name=com_name)
            #return to company profile page
    return render_template('comp_companyform.html')


if __name__ == '__main__':
    app.secret_key = 'cc_key'
    app.run(host='0.0.0.0', port=80, debug=True)
