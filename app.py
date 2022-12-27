from flask import Flask, render_template, request, flash
from flask_mysqldb import MySQL
import smtplib
from datetime import timedelta,date

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["MYSQL_HOST"] = 'localhost'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = '@@Sathyamass08'
app.config["MYSQL_DB"] = 'Flask_app'
mysql = MySQL(app)
smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.login('libarycollege@gmail.com', 'zwbgbvdedsyaoauq')


@app.route('/', methods=['GET', 'POST'])
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
        cur = mysql.connection.cursor()
        Values = name, email, College_ID, book, date_book_purchased, date_book_return, status_book
        cur.execute(
            "INSERT INTO user(name, email ,College_ID ,book, date_book_purchased, date_book_return, status_book)VALUES (%s, %s, %s, %s, %s, %s, %s)",
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
    cur = mysql.connection.cursor()
    user = cur.execute(
        "SELECT email,name,book,date_book_purchased FROM user WHERE date_book_purchased >= CURRENT_DATE AND status_book = 'not submit'")

    if user > 0:
        userDetails = cur.fetchall()
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
        cur = mysql.connection.cursor()
        cur.execute("update user set status_book = %s where name= %s", (paid, Name))
        cur.connection.commit()
        cur.close()
        body = ('Subject: Book Rent From Library.\n\nDear %s,\nYou have rent a '
                'Book from %s,Name of  the Book is %s,'
                'Please make sure to return the book on time. \nThank you!' % (Name))
        print('Sending email to %s...' % Email)
        smtpObj.sendmail('sender email', Email, body)
        smtpObj.quit()
        return "Success"
    return render_template('Book_return.html')


@app.route('/book_details')
def book_details():
    cur = mysql.connection.cursor()
    user = cur.execute(
        "SELECT * FROM user")

    if user > 0:
        userDetails = cur.fetchall()
        return render_template('book_details.html', userDetails=userDetails)


if __name__ == "__main__":
    app.run(debug=True)
