from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pymongo
from pandas import DataFrame
import pandas as pd

app = Flask(__name__)

app.secret_key = 'Your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Your password'
app.config['MYSQL_DB'] = 'restraunts'

mysql = MySQL(app)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["restraunts"]
mycol = mydb["restraunts"]


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            data = list(mycol.find())
            data_rows = []
            for i in data:
                data_rows.append({'Name': i['name'], 'Cuisine': i['cuisine'], 'Street': i['address']['street'], 'Borough': i['borough'], 'Grade': i['grades'][0]['grade']})

            a = pd.DataFrame(data_rows)
            siz = len(a)
            return render_template('main.html', column_names=a.columns.values, row_data=list(a.values.tolist()), zip=zip, size=siz)
        else:
            msg = 'Incorrect username / password!'
    return render_template('login.html', msg=msg)


@app.route("/main", methods=['GET', 'POST'])
def main():
    searchtag = request.form['categories']
    searchvalue = request.form['searchvalue']
    data = list(mycol.find({searchtag: searchvalue}))
    data_rows = []
    for i in data:
        data_rows.append({'Name': i['name'], 'Cuisine': i['cuisine'], 'Street': i['address']['street'], 'Borough': i['borough'], 'Grade': i['grades'][0]['grade']})

    a = pd.DataFrame(data_rows)
    siz = len(a)
    return render_template('main.html', column_names=a.columns.values, row_data=list(a.values.tolist()), zip=zip, size=siz)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)