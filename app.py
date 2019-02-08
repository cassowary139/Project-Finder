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
        return render_template('profile.html',var = [],f = session['fname'], l = session['lname'])
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
            #token = ss.dumps(ee,salt='email-confirm')
            #msgg = Message('Confirm Email', sender='ridamarora89@gmail.com',recipients=[ee])
            #link = url_for('confirm_email',token=token,_external=True)
            #msgg.body = 'Your link is {}'.format(link)
            #mail.send(msgg)
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
@app.route('/confirm_email/<token>')
def confirm_email(token):
    #try:
    ee=ss.loads(token, salt='email-confirm',max_age=3600)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET cusers = 1 WHERE email = %s ", [ee])
    mysql.connection.commit()
    cur.close()
    #cur.execute("UPDATE users SET cusers=1 WHERE email=ee")
    #UPDATE users SET cusers=1 WHERE email=ee
    return 'your email {} is now verified, Thanks for using! :D'.format(ee)
    #return 'Hello world '
    #except SignatureExpired:
        #return '<h1> The token is expired! </h1>'

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
    cur = mysql.connection.cursor()
    print()
    print()
    print()
    print(session['userid'])
    #result = cur.execute('''SELECT code_id,concat(time,date) , nop,inp_file,out_file FROM environment WHERE id = (%s) ''', (user_logged_in ,))
    #result = cur.execute('''SELECT * FROM environment WHERE id = (%s) order by ts desc''', (session['userid'] ,))
    #results = cur.fetchall()
    
    ctr = 0
    par = []
    '''for row in results:
        res = []
        ctr = ctr +1
        res.append(ctr)
        temp1 = row['date']
        temp2 = row['time']
        res.append(temp1+temp2)
        res.append(row['nop'])
        temp3 = row['inp_file']
        temp_file_name = temp3.rfind('/')
        temp_file_name = temp3[temp_file_name+1:]
        link = "../static/inputfiles/" + temp_file_name
        res.append(link)
        res.append(temp_file_name)


        temp4 = row['out_file']
        temp_file_name1 = temp4.rfind('/')
        temp_file_name1 = temp4[temp_file_name1+1:]
        link2 = "../static/images/" + temp_file_name1
        res.append(link2)
        res.append(row['lr'])
        res.append(row['lda'])
        res.append(row['knn'])
        res.append(row['cart'])
        res.append(row['nb'])
        res.append(row['svm'])
        res.append(row['lrv'])
        res.append(row['ldav'])
        res.append(row['knnv'])
        res.append(row['cartv'])
        res.append(row['nbv'])
        res.append(row['svmv'])
        par.append(res)'''
   

    return render_template('profile.html',var = par,f = session['fname'], l = session['lname'])

'''@app.route('/dashboard', methods=['POST'])
def dashboard():
    return render_template('profile.html',f = session['fname'], l = session['lname'])
'''
@app.route('/run', methods= ['POST'])
def run():
    return render_template('user.html',user = session['fname'],var1=0)


@app.route('/input',methods=['GET'])
def input():
    return render_template('input.html')
out_filename = ""
@app.route('/input',methods=['POST'])
def upload():
    
    target = os.path.join(APP_ROOT, 'static/inputfiles/')
    print(target)
    global out_filename
    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "".join([target, filename])
        print(destination)
        file.save(destination)
        num = int(request.form['numOfPar'])
        url = destination
        break

    global nstr
    
   
    out_filename = "/home/sominee/ml/static/images/"
    cur = mysql.connection.cursor()
    cur.execute("SELECT count(*) from environment")
    temp = str(cur.fetchone()['count(*)'])
 
    out_filename+=temp
    out_filename+=".png"
    if not os.path.isfile(out_filename):
        os.mknod(out_filename)
    dataframe = pandas.read_csv(url)
    rows, columns = dataframe.shape
    print()
    print()
    print(columns)
    columns = columns-1
    if  columns != num:
        flash("wrong no. of parameters")
        if session['userid'] == 500:
            return render_template('home.html',var1 = 0)
        else:
            return render_template('user.html',var1 = 0,user = session['fname'])

    
    #dataframe = pandas.read_csv(url)
    array = dataframe.values
    X = array[:,0:num]
    Y = array[:,num]
    
    # prepare configuration for cross validation test harness
    seed = 7
    # prepare models
    models = []
    o1,o2,o3,o4,o5,o6,v1,v2,v3,v4,v5,v6=0,0,0,0,0,0,0,0,0,0,0,0
    if request.form.get("option1"):
        models.append(('LR', LogisticRegression()))
        o1=1
    if request.form.get("option2"):
        models.append(('LDA', LinearDiscriminantAnalysis()))
        o2=1
    if request.form.get("option3"):
        models.append(('KNN', KNeighborsClassifier()))
        o3=1
    if request.form.get("option4"):
        models.append(('CART', DecisionTreeClassifier()))
        o4=1
    if request.form.get("option5"):
        models.append(('NB', GaussianNB()))
        o5=1
    if request.form.get("option6"):
        models.append(('SVM', SVC()))
        o6=1
    
    now  = str(datetime.datetime.now())
    date = now[0:10]
    time1 = now[11:]
    
    print(date,time1)
    
    # evaluate each model in turn
    results = []
    names1 = []
    values = []
    del names1[:]
    scoring = 'accuracy'
    for name, model in models:
        kfold = model_selection.KFold(n_splits=10, random_state=seed)
        cv_results = model_selection.cross_val_score(model, X, Y, cv=kfold, scoring=scoring)
        results.append(cv_results)
        names1.append(name)
        values.append(str(cv_results.mean()))
    ctr = 0
    if o1 == 1:
        v1 = values[ctr]
        ctr+=1
    if o2 == 1:
        v2 = values[ctr]
        ctr+=1
    if o3 == 1:
        v3 = values[ctr]
        ctr+=1
    if o4 == 1:
        v4 = values[ctr]
        ctr+=1
    if o5 == 1:
        v5 = values[ctr]
        ctr+=1
    if o6 == 1:
        v6 = values[ctr]
        ctr+=1
    
    
    templist = []
    templist.append(o1)
    templist.append(o2)
    templist.append(o3)
    templist.append(o4)
    templist.append(o5)
    templist.append(o6)

    templist.append(v1)
    templist.append(v2)
    templist.append(v3)
    templist.append(v4)
    templist.append(v5)
    templist.append(v6)
    xxx = time.time()
    ts = str(int(xxx))
    cur.execute("INSERT INTO environment VALUES(  0, %s,%s, %s,%s, %s,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", ( session['userid'], num , o1 , o2,o3,o4,o5,o6,url,out_filename,time1,date,v1,v2,v3,v4,v5,v6,ts))
    mysql.connection.commit()
    cur.close()
    # boxplot algorithm comparison
    fig=plt.figure(figsize=[6, 6])
    fig.suptitle('Algorithm Comparison')
    ax = fig.add_subplot(111)
    plt.boxplot(results)
    ax.set_xticklabels(names1)

    nstr = temp+".png"           #db.close()
    plt.savefig(out_filename,format = "png")
    plt.close()

    st = "../static/images/"+ nstr
    if session['userid'] == 500:
        return render_template('home.html',var0 = st,var1 = 1,temp = templist)
    else:
        return render_template('user.html',var0 = st,var1 = 1,temp = templist,user = session['fname'])




@app.route('/inputnew',methods=['GET'])
def inputnew():
    return render_template('input.html')
out_filename = ""
@app.route('/inputnew',methods=['POST'])
def uploadnew():
    
    global out_filename
    
    option = request.form['d']
    if option == "A":
        num = 8
        url = "/home/sominee/ml/static/inputfiles/datasets/pima-indians-diabetes.data.csv"
    elif option == "B":
        num = 60
        url = "/home/sominee/ml/static/inputfiles/datasets/sonar.all-data.csv"
    elif option == "C":
        num = 9
        url = "/home/sominee/ml/static/inputfiles/datasets/glass.csv"
    elif option == "D":
        num = 4
        url = "/home/sominee/ml/static/inputfiles/datasets/Banknote.csv"
    elif option == "E":
        num = 3
        url = "/home/sominee/ml/static/inputfiles/datasets/haberman.data"
    elif option == "F":
        num = 11
        url = "/home/sominee/ml/static/inputfiles/datasets/winequality-red.csv"
    else:
        flash('Choose one dataset')
     
    global nstr
   
    out_filename = "/home/sominee/ml/static/images/"
    cur = mysql.connection.cursor()
    cur.execute("SELECT count(*) from environment")
    temp = str(cur.fetchone()['count(*)'])
 
    out_filename+=temp
    out_filename+=".png"
    if not os.path.isfile(out_filename):
        os.mknod(out_filename)
    dataframe = pandas.read_csv(url)
    rows, columns = dataframe.shape
    print()
    print()
    print(columns)
    columns = columns-1
    if  columns != num:
        flash("wrong no. of parameters")
        if session['userid'] == 500:
            return render_template('home.html',var1 = 0)
        else:
            return render_template('user.html',var1 = 0,user = session['fname'])

    
    #dataframe = pandas.read_csv(url)
    array = dataframe.values
    X = array[:,0:num]
    Y = array[:,num]
    
    # prepare configuration for cross validation test harness
    seed = 7
    # prepare models
    models = []
    o1,o2,o3,o4,o5,o6,v1,v2,v3,v4,v5,v6=0,0,0,0,0,0,0,0,0,0,0,0
    if request.form.get("option1"):
        models.append(('LR', LogisticRegression()))
        o1=1
    if request.form.get("option2"):
        models.append(('LDA', LinearDiscriminantAnalysis()))
        o2=1
    if request.form.get("option3"):
        models.append(('KNN', KNeighborsClassifier()))
        o3=1
    if request.form.get("option4"):
        models.append(('CART', DecisionTreeClassifier()))
        o4=1
    if request.form.get("option5"):
        models.append(('NB', GaussianNB()))
        o5=1
    if request.form.get("option6"):
        models.append(('SVM', SVC()))
        o6=1
    
    now  = str(datetime.datetime.now())
    date = now[0:10]
    time1 = now[11:]
    
    print(date,time1)
    
    # evaluate each model in turn
    results = []
    names1 = []
    values = []
    del names1[:]
    scoring = 'accuracy'
    for name, model in models:
        kfold = model_selection.KFold(n_splits=10, random_state=seed)
        cv_results = model_selection.cross_val_score(model, X, Y, cv=kfold, scoring=scoring)
        results.append(cv_results)
        names1.append(name)
        values.append(str(cv_results.mean()))
    ctr = 0
    if o1 == 1:
        v1 = values[ctr]
        ctr+=1
    if o2 == 1:
        v2 = values[ctr]
        ctr+=1
    if o3 == 1:
        v3 = values[ctr]
        ctr+=1
    if o4 == 1:
        v4 = values[ctr]
        ctr+=1
    if o5 == 1:
        v5 = values[ctr]
        ctr+=1
    if o6 == 1:
        v6 = values[ctr]
        ctr+=1
    
    
    templist = []
    templist.append(o1)
    templist.append(o2)
    templist.append(o3)
    templist.append(o4)
    templist.append(o5)
    templist.append(o6)
    templist.append(v1)
    templist.append(v2)
    templist.append(v3)
    templist.append(v4)
    templist.append(v5)
    templist.append(v6)
    xxx = time.time()
    ts = str(int(xxx))
    cur.execute("INSERT INTO environment VALUES(  0, %s,%s, %s,%s, %s,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", ( session['userid'], num , o1 , o2,o3,o4,o5,o6,url,out_filename,time1,date,v1,v2,v3,v4,v5,v6,ts))
    mysql.connection.commit()
    cur.close()
    # boxplot algorithm comparison
    fig=plt.figure(figsize=[6, 6])
    fig.suptitle('Algorithm Comparison')
    ax = fig.add_subplot(111)
    plt.boxplot(results)
    ax.set_xticklabels(names1)

    nstr = temp+".png"           #db.close()
    plt.savefig(out_filename,format = "png")
    plt.close()

    st = "../static/images/"+ nstr
    if session['userid'] == 500:
        return render_template('home.html',var0 = st,var1 = 1,temp = templist)
    else:
        return render_template('user.html',var0 = st,var1 = 1,temp = templist,user = session['fname'])





@app.route('/output',methods=['GET'])
def outpage():
    global nstr
    st = "../static/images/"+ nstr
    return render_template('output.html',var = st)

if __name__ == '__main__':
    app.secret_key = 'sec123'
    app.run(debug=True)