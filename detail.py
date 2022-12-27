# import mysql.connector
# mydb = mysql.connector.connect(
#   host="localhost",
#   user='root',
#   password='@@Sathyamass08',
#   database='Flask_app')
# mycursor = mydb.cursor()
# mycursor.execute("SELECT email,name FROM user WHERE date_book_return <= CURRENT_DATE AND status_book = 'not submit'")
# myresult = mycursor.fetchall()
# for x,y in myresult:
#   print(y)
# from datetime import timedelta,date
# day = date.today()+ timedelta(days=7)
# print(date.today(),day)

from flask import Flask, request, render_template, flash
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        User_Details = request.form
        name = User_Details['name']
        email = User_Details['email']
        College_ID = User_Details['College_ID']
        book = User_Details['book']
        # date_book_purchased = date.today()
        # date_book_return = date.today() + timedelta(days=7)
        # status_book = "'not submit'"
        flash('Login successful')
        return render_template('index.html')
    return render_template('index.html')


app.run(debug=True)