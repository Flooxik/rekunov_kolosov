import sqlite3

def init_db():
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()

    # Создание таблицы фильмов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        release_year INTEGER,
        director TEXT,
        duration INTEGER,
        description TEXT,
        poster_url TEXT
    )
    ''')

    # Создание таблицы пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
    )
    ''')

    # Добавление тестовых данных для пользователей
    cursor.executemany('''
    INSERT OR IGNORE INTO users (username, password, role)
    VALUES (?, ?, ?)
    ''', [
        ('admin', 'admin', 'admin'),
        ('user', 'user', 'user')
    ])

    # Добавление тестовых данных для фильмов
    cursor.executemany('''
    INSERT INTO movies (title, release_year, director, duration, description, poster_url)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        ('Inception', 2010, 'Christopher Nolan', 148, 'A dream heist thriller.', '/static/images/inception.jpg'),
        ('The Matrix', 1999, 'Wachowski Brothers', 136, 'Reality is not what it seems.', '/static/images/matrix.jpg')
    ])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
