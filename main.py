import mysql.connector
from flask import *
import sys
import re
import os
from datetime import *

app = Flask(__name__)
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Welcome@123',
    port='3306',
    database='sujay',
    autocommit=True,
)
mycursor = mydb.cursor()
app.secret_key = os.urandom(24)


@app.before_request
def before_request():
    g.user = None
    if 'pass' in session:
        g.user = session['pass']


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'a' and request.form['username'] == 'a':
            session['pass'] = request.form['password']
            session['user'] = request.form['username']
            return redirect(url_for('table'))

    if request.method == 'POST':
        if request.form['password'] == 'z' and request.form['username'] == 'z':
            session['pass'] = request.form['password']
            session['user'] = request.form['username']
            request.form.username = request.form['username']
            return redirect(url_for('admin'))

    return render_template('login.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        session['subject'] = request.form['subject']
        session['topic'] = request.form['topic']
        session['chapter'] = request.form['chapter']
    return render_template('admin.html')


@app.route('/table', methods=['GET', 'POST'])
def table():
    if g.user:
        mycursor.execute("SELECT ID,Latitude,Longitude FROM table3 WHERE Flag != 1")
        users = mycursor.fetchall()
        return render_template('table.html', user=session['pass'], headings=mycursor.column_names, data=users)
    return redirect(url_for('login'))


@app.route('/refresh', methods=['GET', 'POST'])
def refresh():
    import csv
    report = '3.csv'
    cursor = mydb.cursor()
    with open(report, mode='r') as csv_data:
        reader = csv.reader(csv_data, delimiter=',')
        csv_data_list = list(reader)
    cursor.execute("TRUNCATE table1")
    for row in csv_data_list:
        cursor.execute("""INSERT INTO table1 (uid, Latitude, Longitude) VALUES(%s,%s,%s)""", (row[0], row[1], row[2]))

    cursor.execute("INSERT INTO table3(uid, Latitude, Longitude) SELECT uid, Latitude, Longitude FROM table1 WHERE NOT EXISTS (SELECT 0 FROM table2 WHERE table1.uid = table2.uid AND table1.Latitude = table2.Latitude AND table1.Longitude = table2.Longitude)")  # sujay was here 25/08/2021

    cursor.execute("UPDATE table3 SET Flag = '0';")

    cursor.execute("INSERT INTO table2(uid, Latitude, Longitude) SELECT uid, Latitude, Longitude FROM table1")

    return render_template('refresh.html')

'''
@app.route('/clear', methods=['GET', 'POST'])
def cleartables():
    mycursor.execute(
        "INSERT INTO rawtable2(uid, Latitude, Longitude) SELECT DISTINCT uid, Latitude, Longitude FROM table2")
    mycursor.execute("TRUNCATE table2")
    mycursor.execute("INSERT INTO table2(uid, Latitude, Longitude) SELECT uid, Latitude, Longitude FROM rawtable2")

    mycursor.execute(
        "INSERT INTO rawtable1(uid, Latitude, Longitude) SELECT DISTINCT uid, Latitude, Longitude FROM table1")
    mycursor.execute("TRUNCATE table1")
    mycursor.execute("INSERT INTO table1(uid, Latitude, Longitude) SELECT uid, Latitude, Longitude FROM rawtable1")

    return render_template("refresh.html")  '''


@app.route('/send_data', methods=['GET', 'POST'])
def main():
    global txtFrom
    global txtTo
    # global fname
    username = session['user']
    District = session['subject']
    Taluka = session['topic']
    Village = session['chapter']
    dt = datetime.now()
    txtFrom = request.form['txtFrom']
    txtTo = request.form['txtTo']
    fname = txtFrom + ' to ' + txtTo
    mycursor.execute("UPDATE table3 SET District = '{}' WHERE ID BETWEEN {} AND {}".format(District, txtFrom, txtTo))
    mycursor.execute("UPDATE table3 SET Taluka = '{}' WHERE ID BETWEEN {} AND {}".format(Taluka, txtFrom, txtTo))
    mycursor.execute("UPDATE table3 SET Village = '{}' WHERE ID BETWEEN {} AND {}".format(Village, txtFrom, txtTo))
    mycursor.execute("UPDATE table3 SET Dtime = '{}' WHERE ID BETWEEN {} AND {}".format(dt, txtFrom, txtTo))
    mycursor.execute("UPDATE table3 SET Surveyor = '{}' WHERE ID BETWEEN {} AND {}".format(username, txtFrom, txtTo))
    mycursor.execute("UPDATE table3 SET Flag = 1 WHERE ID BETWEEN {} AND {}".format(txtFrom, txtTo))
    mycursor.execute("SELECT ID, uid, Latitude, Longitude FROM table3 WHERE ID BETWEEN {} AND {};".format(txtFrom, txtTo))
    a = mycursor.fetchall()
    b = re.sub('[Decimal]', '', str(a))
    c = re.sub("[']", '', str(b))
    d = re.sub("['),(]", ' ', str(c))
    with open("C:\\Users\\Administrator\\PycharmProjects\\websitegui\\operation\\10.csv", "w", newline="", encoding="utf-8") as csvfile:
        csvfile.write(d)
    with open(fname + '.csv', 'w', encoding="utf8") as dele:
        dele.write('')
    with open("C:\\Users\\Administrator\\PycharmProjects\\websitegui\\operation\\10.csv", 'r', encoding="utf8") as file:
        for line in file:
            x = 0
            for word in line.split():
                sys.stdout = open(fname + '.csv', 'a', encoding='utf-8')
                print(word, end=' ')
                if x % 4 == 0:
                    print('')
                    x = x + 1
                else:
                    if x % 1 == 0:
                        print(',', end=' ')
                        x = x + 1
                    else:
                        pass
    dele.close()
    mycursor.execute("INSERT INTO table4 SELECT * FROM table3 WHERE ID BETWEEN {} AND {}".format(txtFrom, txtTo))
    mycursor.execute("DELETE FROM table3 WHERE ID BETWEEN {} AND {}".format(txtFrom, txtTo))
    return render_template("download.html", txtFrom=txtFrom, txtTo=txtTo, a=a)


@app.route('/download')
def download_file():
    path = '40.csv'
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run()
    # app.run(host='0.0.0.0', port=5000)
