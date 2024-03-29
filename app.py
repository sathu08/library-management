from flask import Flask, render_template, session, request, flash, redirect,url_for
import secrets
import smtplib
from datetime import timedelta, date
import sqlite3

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.login('libarycollege@gmail.com', 'zwbgbvdedsyaoauq')


@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email_id' in request.form and 'password' in request.form:
        email = request.form['email_id']
        password = request.form['password']
        conn = sqlite3.connect('flask_app.db')
        cur = conn.cursor()
        cur.execute('select * from account WHERE email_id = ? AND password = ?', (email, password))
        account = cur.fetchone()
        cur.connection.commit()
        cur.close()
        if account:
            session['loggedin'] = True
            session['email_id'] = account[0]
            session['password'] = account[1]
            msg = 'Logged in successfully !'
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        User_Details = request.form
        name = User_Details['name']
        email = User_Details['email']
        College_ID = User_Details['College_ID']
        book = User_Details['book']
        date_book_purchased = date.today()
        date_book_return = date.today() + timedelta(days=7)
        status_book = "'not submit'"
        conn = sqlite3.connect('flask_app.db')
        cur = conn.cursor()
        Values = name, email, College_ID, book, date_book_purchased, date_book_return, status_book
        cur.execute(
            "INSERT INTO user(name, email ,College_ID ,book, date_book_purchased, date_book_return, status_book)VALUES (?, ?, ?, ?, ?, ?, ?)",
            (Values))
        cur.connection.commit()
        cur.close()
        body = ('Subject: Book Rent From Library.\n\nDear %s,\nYou have rent a '
                'Book from %s,Name of  the Book is %s,'
                'Please make sure to return the book on time. \nThank you!' % (name, date_book_purchased, book))
        print('Sending email to %s...' % email)
        smtpObj.sendmail('sender email', email, body)
        smtpObj.quit()
        flash('Submitted SuccessFully')
        return render_template('index.html')
    return render_template('index.html')


@app.route('/Sent_mail')
def users():
    conn = sqlite3.connect('flask_app.db')
    cur = conn.cursor()
    cur.execute(
        "SELECT email,name,book,date_book_purchased FROM user WHERE date_book_purchased >= CURRENT_DATE AND status_book = 'not submit'")
    userDetails = cur.fetchall()
    if len(userDetails) >= 0:

        for email, name, book, date_book_purchased in userDetails:
            body = ('Subject: Book Rent From Library Need to Return.\n\nDear %s,\nYou have rent a '
                    'Book from Library on  %s,Name of  the Book is %s,'
                    'Today is the last day to return the Book. \nThank you!') % (name, date_book_purchased, book)
            print('Sending email to %s...' % email)
            sendmailStatus = smtpObj.sendmail('sender email', email, body)
            if sendmailStatus != {}:
                print('There was a problem sending email to %s: %s' % (email, sendmailStatus))
                smtpObj.quit()
        return render_template('Sent_mail.html', userDetails=userDetails)


@app.route('/book_return', methods=['GET', 'POST'])
def book_return():
    if request.method == 'POST':
        User_Details = request.form
        Name = User_Details['name']
        Email = User_Details['email']
        paid = "submit"
        conn = sqlite3.connect('flask_app.db')
        cur = conn.cursor()
        cur.execute("update user set status_book = ? where name= ?", (paid, Name))
        cur.connection.commit()
        cur.close()
        body = ('Subject: Book Rent From Library.\n\nDear %s,\nYou have rent a '
                'Book from ,Name of  the Book is ,'
                'Please make sure to return the book on time. \nThank you!') % Name
        print('Sending email to %s...' % Email)
        smtpObj.sendmail('sender email', Email, body)
        smtpObj.quit()
        flash('Submitted SuccessFully')
        return render_template('Book_return.html')
    return render_template('Book_return.html')


@app.route('/book_details')
def book_details():
    conn = sqlite3.connect('flask_app.db')
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM user")
    userDetails = cur.fetchall()
    if len(userDetails) > 0:

        for i in userDetails:
            print(i)
        return render_template('book_details.html', userDetails=userDetails)
@app.route('/forget_email', methods=['GET','POST'])
def forget_email():
    msg = ''
    if request.method == 'POST':
        user = request.form
        email = user['forgot_email']
        conn = sqlite3.connect('flask_app.db')
        cur = conn.cursor()
        cur.execute('select email_id from account')
        cur.fetchall()
        for i in cur:
            if i[0] == email:
                body = ("Hi! Did you forget your password?\n Click on this link to change your password:"
                        '"http://127.0.0.1:5000/reset_password\n"'
                        '"If you did not request a password reset, then simply ignore this email and no changes will be made."'
                        '"Have a great day!"')
                print('Sending email to %s...' % email)
                smtpObj.sendmail('sender email', email, body)
                smtpObj.quit()
                msg= "Successfully Sent"
                forget_email.var = email
                return render_template('forgot_email.html',msg=msg)
            else:
                msg = 'Incorrect Email'
    return render_template('forgot_email.html',msg=msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    msg = ''
    email = forget_email.var
    if request.method == 'POST':
        password = request.form['password']
        verify_password = request.form['password_verify']
        if password == verify_password:
            conn = sqlite3.connect('flask_app.db')
            cur = conn.cursor()
            cur.execute('update account set password = ? where email_id= ?', (password, email))
            cur.connection.commit()
            cur.close()
            return redirect(url_for('login'))

        else:
            msg = "Password don't match"
    return render_template('reset_password.html', msg=msg)


if __name__ == "__main__":
    app.run(debug=True)
