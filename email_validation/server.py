from flask import Flask, request, redirect, render_template, session, flash
import re
from mysqlconnection import MySQLConnector

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'KeepItSecretKeepItSafe'
mysql = MySQLConnector(app, 'email_validation')

@app.route('/')
def index():
    query = "SELECT * FROM emails"                           # define your query
    email = mysql.query_db(query)                           # run query with query_db()
    return render_template('index.html', all_emails=email) # pass data to our template

@app.route('/email', methods=['POST'])
def create():
    email = request.form['email']

    # print "---------"
    # print len(output)
    # print "---------"

    if len(email) < 1:
        flash("All fields are required!", "error")
    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email Address!", "error")
    else:
        ifexist_query = "SELECT * FROM email_validation.emails WHERE email = :requested_email"
        ifexistData = { 'requested_email': email }

        output = mysql.query_db(ifexist_query, ifexistData)

        if len(output) > 0:
            flash("SORRY MAN, BUT WE ALREADY HAVE THIS EMAILLLL!", "error")
        else:
            query = "INSERT INTO emails (email, created_at, updated_at) VALUES (:email, NOW(), NOW())"
            data = { 'email': email }
            mysql.query_db(query, data)
            flash("Thanks for submitting your information", "success")        

    return redirect('/')


@app.route('/emails/<email_id>')
def show(email_id):

    query = "SELECT * FROM emails WHERE id = :email_id"
    data = {'email_id': email_id}

    email = mysql.query_db(query, data)
    if len(email) > 0:
        return render_template('index.html', one_email=email[0])
    else:
        return redirect('/')


@app.route('/update_email/<email_id>', methods=['POST'])
def update(email_id):
    query = "UPDATE emails SET email = :email WHERE id = :id"
    data = {
             'email': request.form['email'],
             'id': email_id
           }
    mysql.query_db(query, data)
    return redirect('/')


@app.route('/remove_email/<email_id>')
def delete(email_id):
	query = "DELETE FROM emails WHERE id = :id"
	data = {'id': email_id}
	mysql.query_db(query, data)
	return redirect('/')


app.run(debug=True)