import sqlite3
from cachelib import FileSystemCache
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, redirect, url_for, flash, session, redirect, url_for
from future.backports.datetime import timedelta

from flask_session import Session
import os
curr_path=os.path.dirname(__file__)
os.chdir(curr_path)
conn = sqlite3.connect('data.db', check_same_thread=False)
cursor = conn.cursor()

app = Flask(__name__)
app.secret_key = '1234'
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
Session(app)



@app.route('/')
def main():
    cursor.execute('SELECT * FROM info')
    data = cursor.fetchall()
    return render_template('main.html', data=data)

@app.route('/about/', methods=['POST', 'GET'])
def a_about():
    return render_template('about.html')

@app.route('/buy/')
def buy():
    return render_template('buy.html')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    cursor.execute("SELECT * FROM data WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if product:
        return render_template("veteran.html", product=product)
    else:
        return "Товар не найден", 404

@app.route('/street/<int:street_id>')
def street_detail(street_id):
    cursor.execute("SELECT * FROM street WHERE id = ?", (street_id,))
    street = cursor.fetchone()
    if street:
        return render_template("street.html", street=street)
    else:
        return "улица не найдена", 404

@app.route('/info/<int:info_id>')
def info_detail(info_id):
    cursor.execute("SELECT * FROM info WHERE id = ?", (info_id,))
    info = cursor.fetchone()
    if info:
        return render_template("info.html", info=info)
    else:
        return "улица не найдена", 404

@app.route('/register/', methods=['POST', 'GET'])
def page_reg():
    return render_template('register.html')

@app.route('/login/')
def login():
    data = cursor.fetchall()
    return render_template('login.html',data=data)

@app.route('/streets/')
def streets():
    cursor.execute('SELECT * FROM street')
    data = cursor.fetchall()
    return render_template('streets.html', data=data)

@app.route('/admin_street/')
def admin_street():
    cursor.execute('SELECT * FROM street')
    data = cursor.fetchall()
    return render_template('admin_street.html', data=data)

@app.route('/veterans/')
def veterans():
    cursor.execute('SELECT * FROM data')
    data= cursor.fetchall()
    return render_template('veterans.html', data=data)

@app.route('/admin_veterans/')
def admin_veterans():
    cursor.execute('SELECT * FROM data')
    data = cursor.fetchall()
    return render_template('admin_veterans.html', data=data)



@app.route('/admin_main/')
def admin_main():
    cursor.execute('SELECT * FROM info')
    data = cursor.fetchall()
    return render_template('admin_main.html', data=data)



@app.route('/search/')
def search_page():
    cursor.execute('SELECT * FROM data')
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM street')
    street = cursor.fetchall()
    return render_template('search.html', data=data, street=street)

@app.route('/search/result_find/')
def result_find_page():
    type_find = request.args.get('type_find')
    text_find = request.args.get('text')
    cursor.execute(f'SELECT * FROM data WHERE {type_find}=?', [text_find])
    data = cursor.fetchall()
    cursor.execute(f'SELECT * FROM street WHERE {type_find}=?', [text_find])
    street = cursor.fetchall()
    return render_template('result_find.html', data=data, street=street)





@app.route('/save_register/', methods=['POST', "GET"])
def save_reg():
    if request.method == 'POST':
        last_name = request.form['last_name']
        name = request.form['name']
        patronymic = request.form['patronymic']
        gender = request.form['gender']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        cursor.execute(f'INSERT INTO autorisation (last_name, name, patronymic, gender, email, username, password) VALUES (?,?,?,?,?,?,?)',
                        [last_name, name, patronymic, gender, email, username, password])
        conn.commit()
        return redirect(url_for('login'))

@app.route('/authorization/', methods=['GET', 'POST'])
def autorisation():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password']

        cursor.execute('select username, password from autorisation where username=(?) and password=(?)',[login, password])
        data = cursor.fetchall()

        if len(data) != 0:
            session['login'] = True
            session['username'] = login
            session.permanent = False
            app.permanent_session_lifetime = timedelta(minutes=1)
            session.modified = True
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('admin_main'))
        else:
            flash('неправильный логин или пароль', 'danger')
            return redirect(url_for('login'))


@app.route('/add/')
def add():
    #if 'login' not in session:
    #    flash('Необ')
    return render_template('add.html')

@app.route('/add_street/')
def add_street():
    return render_template('add_street.html')

@app.route('/upload_street/', methods=['POST'])
def save_streets():
    image = request.files.get('image')
    title = request.form['title']
    file_name = f'uploads_street/{image.filename}'
    image.save(f'static/{file_name}')
    description = request.form['description']
    cursor.execute(f'INSERT INTO street (title, file_name, description ) VALUES (?,?,?)',
                        [title, file_name, description])
    conn.commit()
    return redirect(url_for('admin_street'))

@app.route('/upload/', methods=['POST'])
def save_post():
    image = request.files.get('image')
    title = request.form['title']
    file_name = f'uploads/{image.filename}'
    description = request.form['description']
    image.save(f'static/{file_name}')
    cursor.execute(f'INSERT INTO data (title, file_name, description) VALUES (?,?,?)',
                        [title, file_name, description])
    conn.commit()
    return redirect(url_for('admin_veterans'))

@app.route('/a_about/', methods=['POST', 'GET'])
def about():
    return render_template('a_about.html')

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item_veterans(item_id):
    try:
        # SQL query to delete the item from the database
        cursor.execute('DELETE FROM data WHERE id = ?', (item_id,))
        conn.commit()
        flash('Товар успешно удалён!', 'success')  # Flash success message
    except Exception as e:
        flash('Ошибка при удалении товара!', 'danger')  # Flash error message
        print(f"Ошибка: {e}")
    return redirect(url_for('admin_veterans'))

@app.route('/delete_street/<int:street_id>', methods=['POST'])
def delete_item_street(street_id):
    try:
        # SQL query to delete the item from the database
        cursor.execute('DELETE FROM street WHERE id = ?', (street_id,))
        conn.commit()
        flash('Товар успешно удалён!', 'success')  # Flash success message
    except Exception as e:
        flash('Ошибка при удалении товара!', 'danger')  # Flash error message
        print(f"Ошибка: {e}")
    return redirect(url_for('admin_street'))

@app.route('/delete_info/<int:info_id>', methods=['POST'])
def delete_item_info(info_id):
    try:
        # SQL query to delete the item from the database
        cursor.execute('DELETE FROM info WHERE id = ?', (info_id,))
        conn.commit()
        flash('Товар успешно удалён!', 'success')  # Flash success message
    except Exception as e:
        flash('Ошибка при удалении товара!', 'danger')  # Flash error message
        print(f"Ошибка: {e}")
    return redirect(url_for('admin_info'))

@app.route('/admin_main/')
def admin_info():
    cursor.execute('SELECT * FROM info')
    data = cursor.fetchall()
    return render_template('admin_main.html', data=data)

@app.route('/add_info/')
def add_info():
    return render_template('add_info.html')


@app.route('/upload_info/', methods=['POST'])
def save_info():
    images = request.files.getlist('image')
    title = request.form['title']
    description = request.form['description']

    # Проходим по каждому изображению в списке
    for img in images:
        # Безопасно формируем имя файла
        filename = secure_filename(img.filename)
        file_path = f'uploads_info/{filename}'

        # Сохраняем изображение по указанному пути
        img.save(f'static/{file_path}')

        # Вставляем информацию об изображении в базу данных
        cursor.execute('INSERT INTO info (title, file_name, description) VALUES (?, ?, ?)',
                       [title, file_path, description])

    conn.commit()
    return redirect(url_for('admin_main'))

@app.route("/logout/")
def logout():
    session.clear()
    flash('Вы вышли из профиля', 'danger')
    return redirect(url_for("main"))

