import os
from flask import Flask, render_template,flash, request, redirect, url_for, session, request,logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
import csv
from flask_mail import Mail, Message
import itsdangerous

import pandas
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import calendar
import time
import datetime
from flask_mysqldb import MySQL



app = Flask(__name__)

nstr=""

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'iiita123'
app.config['MYSQL_DB'] = 'sheshacks'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.config.from_pyfile('config.cfg')
mail =Mail(app)
mysql = MySQL(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def index():
    #session['userid'] = 500
    #session['logged_in'] = False
    # session['username'] = ""
    # session['fname'] = ""
    # session['lname'] = ""
    if session.get('logged_in') == True :
        return render_template('user.html',user = session['fname'],var1=0)
    else :
        return render_template('home.html',var0 = 0,var1 = 0,temp = 0)

ss = itsdangerous.URLSafeTimedSerializer('Secret!')

@app.route('/register', methods = ['GET' , 'POST'])
def register():
        if request.method == 'POST':
            ff = (request.form['fname'])
            ll = (request.form['lname'])
            ee = (request.form['email'])
            pp = (request.form['pass'])
            cp = (request.form['confirm'])
            num = int(0)

            print("%s,%s,%s,%s" % (ff,ll,ee,pp))
            cur1 = mysql.connection.cursor()
            result = cur1.execute('''SELECT * FROM users where email = (%s)''',(ee,))
            if result>0 :
                flash('Email Already Exists! Register again!')
                return redirect(url_for('index')) 
            else:
                if pp == cp:
                    cur = mysql.connection.cursor()
                    password = sha256_crypt.encrypt(pp)
                    cur.execute("INSERT INTO users (id, fname, lname, email,pass) VALUES( 0, %s, %s, %s, %s)", ( ff , ll , ee , password))
                    mysql.connection.commit()
                    cur.close()

                    #win32api.MessageBox(0, 'hello', 'title')
                    flash('Registered Successfully! Please Login')
                    return redirect(url_for('index'))  
                else:
                    flash('Your Passwords Do not match')
        
        return redirect(url_for('index'))

@app.route('/results', methods = ['GET', 'POST'])
def results():
    if request.method == 'POST' : 
        print(request.form)
        se = str(request.form['search'])
        ca = str(request.form['choices-single-defaul'])
        cur = mysql.connection.cursor()

        if ca == 'Project':
            sql = """SELECT * FROM projects where title like %s"""
            result = cur.execute(sql, (('% ' + se + ' %',)))
            #result = cur.execute('''SELECT * FROM projects where title like %% %s %%''',(se,))
        elif ca == 'User' :
            sql = """SELECT * FROM users where user_id like %s"""
            result = cur.execute(sql, (('%' + se + '%',)))
            #result = cur.execute('''SELECT * FROM projects where user_id like %%%s%%''',(se,))
        else :
            sql = """SELECT * FROM projects where tags like %s"""
            result = cur.execute(sql, (('%' + se + '%',)))
            #result = cur.execute('''SELECT * FROM projects where tags like %%%s%%''',(se,))
        rows = []

        if result > 0 : 
            data = cur.fetchall()
            for row in cur:
                new_row = []
                new_row.append(row['title'])
                new_row.append(row['description'])
                uid = row['user_id']
                cur1 = mysql.connection.cursor()
                r = cur1.execute('''SELECT * FROM users where id = (%s)''',(uid,))
                res = cur1.fetchone()
                nm = str(res['fname']) + " " + str(res['lname'])
                cur1.close()
                new_row.append(nm)
                new_row.append(row['user_id'])
                if row['stat'] == 0:
                    new_row.append('Past')
                elif row['stat'] == 1 :
                    new_row.append('Ongoing')
                else : 
                    new_row.append('Future')
                rows.append(new_row)

        return render_template('results.html', query = se, data = rows)

    else :
        return render_template('results.html', data = [])


@app.route('/addProject', methods = ['GET' , 'POST'])
def addProject():
        if request.method == 'POST':
            ti = str((request.form['title']))
            de = str((request.form['description']))
            ta = str((request.form['tags']))
            pa = (request.form['option'])
            user = session['userid']


            print("%s,%s,%s,%s" % (ti,de,ta,pa))
            cur1 = mysql.connection.cursor()
            if pa == "ongoing" : 
                num = 1
            elif pa == "past":
                num = 0
            else:
                num = 2
            
            print(type(user))
            print(type(ti))
            print(type(de))
            print(type(num))
            print(type(ta))
            
            cur1.execute("INSERT INTO projects VALUES( 0, %s, %s, %s, %s,%s)", ( user , ti , de , num , ta))
            mysql.connection.commit()
            cur1.close()
        
        return redirect(url_for('dashboard'))

@app.route('/editdetails', methods = ['GET' , 'POST'])
def editdetails():
        if request.method == 'POST':
            bio = str((request.form['bio']))
            git = str((request.form['git']))
            lin = str((request.form['lin']))
            sk = str((request.form['skills']))
            user = session['userid']


            print("%s,%s,%s,%s" % (bio,git,lin,sk))
            cur1 = mysql.connection.cursor()
            
            cur1.execute("UPDATE users SET bio = %s, skills = %s,github = %s, linkedin= %s WHERE id =%s", ( bio , git ,lin , sk,user ) )
            mysql.connection.commit()
            cur1.close()
        
        return redirect(url_for('index'))



@app.route('/login', methods = ['GET' , 'POST'])
def login():
    username = ''
    fname = ''
    lname = ''
    idd = 500
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['pass']
        
        fname = ''
        

        cur = mysql.connection.cursor()
        result = cur.execute('''SELECT * FROM users WHERE email = (%s) ''', (email ,))
        
        if result>0 :
            data = cur.fetchone()
            fname = data['fname']
            lname = data['lname']
            idd = data['id']
            username = fname+ lname
            password = data['pass']
            #cusers = data['cusers']
            if sha256_crypt.verify(password_candidate, password): 
            #if cusers ==1:
                session['logged_in'] = True
                session['username'] = username
                session['fname'] = fname
                session['lname'] = lname
                session['userid'] = idd
                app.logger.info('PASSWORD is a match %s',(username))
                return render_template('user.html', user = fname,var1=0 )
                #else:
                    #flash("Please confirm your mail!")
                    #return redirect(url_for('index'))

            else:
                app.logger.info('Wrong password!');
                flash("Wrong password!")
                #return render_template('home.html',var0 = 0,var1 = 0,temp = 0)
                return redirect(url_for('index'))
        else:
            session['userid'] = 500
            session['logged_in'] = False
            session['username'] = ""
            session['fname'] = ""
            session['lname'] = ""

            app.logger.info('NO user')
            error = 'Invalid Credentials'
            return redirect(url_for('index'))


@app.route('/logout',methods =['POST'])
def logout():
    session['logged_in'] = False
    

    return redirect(url_for('index'))


   
@app.route('/dashboard', methods=['POST'])
def dashboard():
    if session['logged_in'] == False : 
        return redirect(url_for('index'))
        #return render_template('home.html',var0 = 0,var1 = 0,temp = 0)
    cur = mysql.connection.cursor()
    i = session['userid']
    result = cur.execute('''SELECT * FROM users where id =(%s)''',(i,))
   
    row = cur.fetchone() 
    em = row['email']
    bio = row['bio']
    git = row['github']
    linkedin = row['linkedin']
    sk = row['skills']
    cur.close()

    cur1 = mysql.connection.cursor()
    result = cur1.execute('''SELECT * FROM projects where user_id =(%s)''',(i,))
    results = cur1.fetchall()
    par =[]

    for row in results:
        res = []
        res.append(row['title'])
        res.append(row['description'])
        if(row['stat'] == 0):
            res.append('Past')
        elif(row['stat'] == 1):
            res.append('Ongoing')
        else :
            res.append('Future Idea')
        par.append(res)

    return render_template('profile.html',var = par,f = session['fname'], l = session['lname'],email = em,bio = bio,git = git,linkedin = linkedin,skill =sk )
@app.route('/profile/<userid>')
def profile(userid):
    cur = mysql.connection.cursor()
    result = cur.execute('''SELECT * FROM users where id = (%s)''',(userid,))
    
    row = cur.fetchone() 

    em = row['email']
    bio = row['bio']
    git = row['github']
    linkedin = row['linkedin']
    sk = row['skills']
    fn = row['fname']
    ln = row['lname']
    cur.close()
    cur1 = mysql.connection.cursor()
    result = cur1.execute('''SELECT * FROM projects where user_id =(%s)''',(userid,))
    results = cur1.fetchall()
    par =[]

    for prow in results:
        res = []
        res.append(prow['title'])
        res.append(prow['description'])
        if(prow['stat'] == 0):
            res.append('Past')
        elif(prow['stat'] == 1):
            res.append('Ongoing')
        else :
            res.append('Future Idea')
        par.append(res)


    
    ctr = 0
    print(userid)
    print(session['userid'])
    if userid != session['userid'] :
        return render_template('otherprofile.html',var = par,f = fn, l = ln,email = em,bio = bio,git = git,linkedin = linkedin,skill =sk )
    else :
        return redirect(url_for('dashboard'))

'''@app.route('/dashboard', methods=['POST'])
def dashboard():
    return render_template('profile.html',f = session['fname'], l = session['lname'])
'''


if __name__ == '__main__':
    app.secret_key = 'sec123'
    app.run(debug=True)