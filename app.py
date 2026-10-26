from flask import Flask, url_for, render_template, redirect, request
import mysql.connector
import os

app = Flask(__name__)


UPLOAD_FOLDER = 'static/people'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


con = mysql.connector.connect(
    host='localhost',
    user='root',
    password='didar09k',
    database='cai'
)

cursor = con.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    surname VARCHAR(100),
    mobile VARCHAR(100),
    photo_path VARCHAR(255)
);
''')
cursor.close()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name'].strip()
    surname = request.form['surname'].strip()
    mobile = request.form['mobile'].strip()

    photo = request.files['photo']

    if photo:
       
        filename = f"{surname}_{name}.png"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(save_path)

        
        photo_path = f"people/{filename}"

       
        cursor = con.cursor()
        sql = 'INSERT INTO user (name, surname, mobile, photo_path) VALUES (%s, %s, %s, %s)'
        cursor.execute(sql, (name, surname, mobile, photo_path))
        con.commit()
        cursor.close()

    return redirect(url_for('good'))


@app.route('/good')
def good():
    return render_template('good.html')


if __name__ == '__main__':
    app.run(debug=True)
