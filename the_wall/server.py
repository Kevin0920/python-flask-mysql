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
mysql = MySQLConnector(app, 'wall')

@app.route('/')
def index():
    # query = "SELECT * FROM users"                           # define your query
    # email = mysql.query_db(query)                           # run query with query_db()
    return render_template('index.html', bla=redirect('/')) 

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
                print output

                session['user_id'] = output[0][u'id']
                hashstring = str(output[0][u'id']) + str(output[0][u'email'])
                
                session['key'] = md5.new(hashstring).hexdigest()
                return redirect("/wall")
            else:
                print md5.new(password + salt).hexdigest()
                flash("Password doesn't match, try again", "error")
        elif len(output) == 0:
            flash("SORRY MAN, WE DON'T HAVE YOUR EMAIL IN Data Base", "error")

        
    return redirect('/')

@app.route('/wall')
def wall():

    if "key" in session and "user_id" in session:
        key = session['key']
        uid = session['user_id']
        # Making query into DB
        # What messages do we have
        # allmsags = "SELECT messages.id, users.first_name, users.last_name, messages.created_at, messages.message, messages.user_id FROM messages JOIN users ON messages.user_id = users.id"
        allmsags = "SELECT messages.id, users.first_name, users.last_name, messages.created_at, messages.message, messages.user_id  FROM messages LEFT JOIN users ON messages.user_id = users.id"
        all_messages = mysql.query_db(allmsags)

        allcomments = "SELECT comments.comment, comments.created_at, comments.message_id, comments.user_id, users.first_name, users.last_name  FROM comments LEFT JOIN users ON comments.user_id = users.id"
        all_comments = mysql.query_db(allcomments)
        # User info
        ifexist_query = "SELECT * FROM users WHERE id = :requested_id "
        ifexistData = { 'requested_id': uid }
        output = mysql.query_db(ifexist_query, ifexistData)

        # Generating from our query key for check
        hashstring = str(output[0][u'id']) + str(output[0][u'email'])
        hashkey = md5.new(hashstring).hexdigest()

        # Checking if our fetched key is the same like in session
        if key == hashkey:

            fname = str(output[0][u'first_name']) + " " + str(output[0][u'last_name'])

            return render_template('wall.html',fname=fname, all_messages=all_messages, all_comments=all_comments) 
    else:
        flash("SORRY MAN, Your session EXPIRED! Login again", "error")
        return redirect('/')

@app.route('/post_message', methods=["POST"])
def post_message():
# INSERT INTO `wall`.`messages` (`id`, `message`, `created_at`, `updated_at`, `user_id`) VALUES ('1', 'Hello dude!', '2', '2', '1');

    query = "INSERT INTO messages (message, created_at, updated_at, user_id) VALUES ( :message, NOW(), NOW(), :user_id )"
    data = { 
            'message': str(request.form['message_text']),
            'user_id': session['user_id']
    }
    output = mysql.query_db(query, data)
    flash("Your message was posted", "success")
    return redirect("/wall")

@app.route('/post_comment', methods=["POST"])
def post_comment():

    query = "INSERT INTO comments (comment, created_at, user_id, message_id) VALUES ( :comment, NOW(), :user_id, :message_id )"
    data = { 
            'comment': str(request.form['comment_text']),
            'user_id': request.form['user_id'],
            'message_id': request.form['message_id']
    }
    output = mysql.query_db(query, data)
    return redirect("/wall")

@app.route('/logoff')
def logoff():
    del session['user_id']
    del session['key']
    return redirect('/') 

app.run(debug=True)