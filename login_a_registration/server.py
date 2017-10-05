from flask import Flask, request, redirect, render_template, session, flash
import re
from mysqlconnection import MySQLConnector
import md5
import os, binascii

# Making SALT
salt = binascii.b2a_hex("Hs4lds8weDS")

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'KeepItSecretKeepItSafe'
mysql = MySQLConnector(app, 'logregisterbasse')

@app.route('/')
def index():
    # query = "SELECT * FROM users"                           # define your query
    # email = mysql.query_db(query)                           # run query with query_db()
    return render_template('index.html') 

@app.route('/register', methods=['POST'])
def create():

    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    password = request.form['password']

    repassword = request.form['repassword']

    # Hashed stuff
    hashed_password = md5.new(password).hexdigest()
    print hashed_password

    # Hashed with salt
    hashed_pw_w_salt = md5.new(password + salt).hexdigest()
    print hashed_pw_w_salt
    # Hashed stuff

    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
    data = { 
            'first_name': fname,
            'last_name': lname,
            'email': email,
            'password': hashed_pw_w_salt
    }


    if len(email) < 1 or len(fname) < 1 or len(lname) < 1 or len(password) < 1:
        flash("You can't leave empty field(s)!", "error")
        return redirect('/')
    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email Address!", "error")
        return redirect('/')
    elif password != repassword:
        flash("Passwords don't match!", "error")
        return redirect('/')
    elif lname.isalpha() == False or fname.isalpha() == False:
        flash("Name and Last name should be alphabetical!", "error")
        return redirect('/')
    else:
        ifexist_query = "SELECT * FROM users WHERE email = :requested_email"
        ifexistData = { 'requested_email': email }
        output = mysql.query_db(ifexist_query, ifexistData)

        if len(output) > 0:
            flash("SORRY MAN, BUT WE ALREADY HAVE THIS EMAILLLL!", "error")
            return redirect('/')
        else:
            mysql.query_db(query, data)
            flash("Thanks for submitting your information", "success")
        
    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']


    if len(email) < 1 or len(password) < 1:
        flash("You can't leave empty field(s)!", "error")
        return redirect('/')
    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email Address!", "error")
        return redirect('/')
    else:
        ifexist_query = "SELECT * FROM users WHERE email = :requested_email"
        ifexistData = { 'requested_email': email }
        output = mysql.query_db(ifexist_query, ifexistData)
        if len(output)>0:
            if output[0][u'password'] == md5.new(password + salt).hexdigest():
                return redirect("/success")
            else:
                print md5.new(password + salt).hexdigest()
                flash("Password doesn't match, try again", "error")
        elif len(output) == 0:
            flash("SORRY MAN, WE DON'T HAVE YOUR EMAIL IN Data Base", "error")

        
    return redirect('/')

@app.route('/success')
def success():

    return render_template('success.html') 

app.run(debug=True)