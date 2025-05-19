import sqlite3
from cachelib import FileSystemCache

from flask import Flask, render_template, request, redirect, url_for, flash, session, redirect, url_for
from future.backports.datetime import timedelta

from flask_session import Session
conn = sqlite3.connect('data.db', check_same_thread=False)
cursor = conn.cursor()

app = Flask(__name__)
app.secret_key = '1234'
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
Session(app)



@app.route('/')
def main():
    cursor.execute('SELECT * FROM data')
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
        return render_template("product.html", product=product)
    else:
        return "Товар не найден", 404


@app.route('/reviews/', methods=['POST', 'GET'])
def reviews():
    cursor.execute('SELECT * FROM reviews')
    data = cursor.fetchall()
    return render_template('reviews.html', data=data)

@app.route('/register/', methods=['POST', 'GET'])
def page_reg():
    return render_template('register.html')

@app.route('/login/')
def login():
    data = cursor.fetchall()
    return render_template('login.html',data=data)

@app.route('/admin_main/')
def admin_main():
    cursor.execute('SELECT * FROM data')
    data = cursor.fetchall()
    return render_template('admin_main.html', data=data)

@app.route('/admin_reviews/')
def admin_reviews():
    cursor.execute('SELECT * FROM reviews')
    data = cursor.fetchall()
    return render_template('admin_reviews.html', data=data)



@app.route('/add_reviews/')
def add_reviews():
    #if 'login' not in session:
    #    flash('Необ')
    return render_template('add_reviews.html')

@app.route('/search/')
def search_page():
    cursor.execute('SELECT * FROM data')
    data = cursor.fetchall()
    return render_template('search.html', data=data)

@app.route('/search/result_find/')
def result_find_page():
    type_find = request.args.get('type_find')
    text_find = request.args.get('text')
    cursor.execute(f'SELECT * FROM data WHERE {type_find}=?', [text_find])
    data = cursor.fetchall()
    return render_template('result_find.html', data=data)





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

@app.route('/upload_reviews/', methods=['POST'])
def save_reviews():
    image = request.files.get('image')
    title = request.form['title']
    file_name = f'uploads_reviews/{image.filename}'
    image.save(f'static/{file_name}')
    description = request.form['description']
    cursor.execute(f'INSERT INTO reviews (title, file_name, description ) VALUES (?,?,?)',
                        [title, file_name, description])
    conn.commit()
    return redirect(url_for('reviews'))

@app.route('/upload/', methods=['POST'])
def save_post():
    image = request.files.get('image')
    title = request.form['title']
    file_name = f'uploads/{image.filename}'
    description = request.form['description']
    image.save(f'static/{file_name}')
    price = request.form['price']
    brand = request.form['brand']
    cursor.execute(f'INSERT INTO data (title, file_name, description, price, brand) VALUES (?,?,?,?,?)',
                        [title, file_name, description, price, brand])
    conn.commit()
    return redirect(url_for('admin_main'))

@app.route('/a_about/', methods=['POST', 'GET'])
def about():
    return render_template('a_about.html')

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item_tovar(item_id):
    try:
        # SQL query to delete the item from the database
        cursor.execute('DELETE FROM data WHERE id = ?', (item_id,))
        conn.commit()
        flash('Товар успешно удалён!', 'success')  # Flash success message
    except Exception as e:
        flash('Ошибка при удалении товара!', 'danger')  # Flash error message
        print(f"Ошибка: {e}")
    return redirect(url_for('admin_main'))

@app.route('/delete_reviews/<int:item_id>', methods=['POST'])
def delete_item_reviews(item_id):
    try:
        # SQL query to delete the item from the database
        cursor.execute('DELETE FROM reviews WHERE id = ?', (item_id,))
        conn.commit()
        flash('Товар успешно удалён!', 'success')  # Flash success message
    except Exception as e:
        flash('Ошибка при удалении товара!', 'danger')  # Flash error message
        print(f"Ошибка: {e}")
    return redirect(url_for('admin_reviews'))

@app.route("/logout/")
def logout():
    session.clear()
    flash('Вы вышли из профиля', 'danger')
    return redirect(url_for("main"))

app.run(debug=True)