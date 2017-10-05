from flask import Flask
# import the Connector function
from mysqlconnection import MySQLConnector
app = Flask(__name__)
# connect and store the connection in "mysql" note that you pass the database name to the function
mysql = MySQLConnector(app, 'sakila')
# an example of running a query

query = 'SELECT city.city_id, city.city, customer.first_name, customer.last_name, customer.email, address.address'
query += ' FROM city'
query += ' LEFT JOIN address'
query += ' ON city.city_id = address.city_id'
query += ' LEFT JOIN customer'
query += ' ON address.address_id = customer.address_id'
query += ' WHERE city.city_id = 312;'
print mysql.query_db(query)
app.run(debug=True)
