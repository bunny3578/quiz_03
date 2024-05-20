from flask import (
    Flask,
    session,
    redirect,
    url_for,
    render_template,
    request,
    g
)
import logging
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'mysecretkey'
DB_NAME = 'mydb.db'

logging.basicConfig(filename='error.log', level=logging.ERROR)


@app.before_request
def before_request():
    try:
        if not os.path.exists(DB_NAME):
            raise FileNotFoundError(f"Database file {DB_NAME} does not exist.")
        g.conn = sqlite3.connect(DB_NAME)
        g.conn.row_factory = sqlite3.Row
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None


@app.teardown_appcontext
def teardown(exception):
    conn = getattr(g, 'conn', None)
    if conn is not None:
        conn.close()


def get_user_data(idno):
    try:
        cursor = g.conn.cursor()
        cursor.execute("SELECT * FROM member WHERE idno = ?", (idno,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        logging.error(f"Error in get_user_data: {e}")
        return None


def update_user_data(idno, form_data):
    try:
        cursor = g.conn.cursor()
        cursor.execute(
            """
            UPDATE member
            SET nm = ?, birth = ?, blood = ?,
                phone = ?, email = ?, idno = ?, pwd = ?
            WHERE idno = ?
            """,
            (
                form_data['nm'],
                form_data['birth'],
                form_data['blood'],
                form_data['phone'],
                form_data['email'],
                form_data['idno'],
                form_data['pwd'],
                idno
            )
        )
        g.conn.commit()
        session['username'] = form_data['idno']
    except Exception as e:
        logging.error(f"Error in update_user_data: {e}")


@app.route('/')
def index():
    if 'username' in session:
        user_data = get_user_data(session['username'])
        if user_data:
            return render_template('index.html', user=user_data)
        else:
            return render_template('error.html')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            idno = request.form.get('idno')
            password = request.form.get('pwd')
            cursor = g.conn.cursor()
            cursor.execute(
                "SELECT * FROM member WHERE idno = ? AND pwd = ?",
                (idno, password)
            )
            user = cursor.fetchone()
            if user:
                session['username'] = idno
                return redirect(url_for('index'))
            else:
                error = "請輸入正確的帳號密碼"
        except Exception as e:
            logging.error(str(e))
    return render_template('login.html', error=error)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'username' in session:
        try:
            if request.method == 'POST':
                update_user_data(session['username'], request.form)
            user_data = get_user_data(session['username'])
            if user_data:
                return render_template('edit.html', user=user_data)
            else:
                return render_template('error.html')
        except Exception as e:
            logging.error(str(e))
            return render_template('error.html')
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
