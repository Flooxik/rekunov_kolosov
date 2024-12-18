
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Для защиты сессий

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('cinema.db')
    conn.row_factory = sqlite3.Row
    return conn

# Проверка роли пользователя
def check_admin():
    return 'user_role' in session and session['user_role'] == 'admin'

# Главная страница: список фильмов с поиском
@app.route('/')
def index():
    # Если пользователь не авторизован, перенаправляем на страницу входа
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search_query = request.args.get('q', '')  # Поисковый запрос
    conn = get_db_connection()
    if search_query:
        movies = conn.execute(
            'SELECT * FROM movies WHERE title LIKE ?', (f'%{search_query}%',)
        ).fetchall()
    else:
        movies = conn.execute('SELECT * FROM movies').fetchall()
    conn.close()
    return render_template('index.html', movies=movies, search_query=search_query)

# Авторизация: вход
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?', (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials!')
    return render_template('login.html')

# Авторизация: выход
@app.route('/logout')
def logout():
    session.clear()  # Очистка сессии
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

# Подробная информация о фильме
@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    conn = get_db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()
    conn.close()
    if not movie:
        return "Movie not found", 404
    return render_template('movie_details.html', movie=movie)

# Добавление нового фильма (админ)
@app.route('/admin/movie/add', methods=('GET', 'POST'))
def add_movie():
    if not check_admin():
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['release_year']
        director = request.form['director']
        duration = request.form['duration']
        description = request.form['description']
        poster_url = request.form['poster_url']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO movies (title, release_year, director, duration, description, poster_url) VALUES (?, ?, ?, ?, ?, ?)',
            (title, release_year, director, duration, description, poster_url)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_movie.html')

# Редактирование фильма (только для админа)
@app.route('/admin/movie/edit/<int:movie_id>', methods=('GET', 'POST'))
def edit_movie(movie_id):
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('You do not have permission to edit movies.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()

    if not movie:
        conn.close()
        return "Movie not found", 404

    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['release_year']
        director = request.form['director']
        duration = request.form['duration']
        description = request.form['description']
        poster_url = request.form['poster_url']

        conn.execute('''
        UPDATE movies
        SET title = ?, release_year = ?, director = ?, duration = ?, description = ?, poster_url = ?
        WHERE id = ?
        ''', (title, release_year, director, duration, description, poster_url, movie_id))
        conn.commit()
        conn.close()

        flash('Movie details updated successfully!')
        return redirect(url_for('movie_details', movie_id=movie_id))

    conn.close()
    return render_template('edit_movie.html', movie=movie)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
