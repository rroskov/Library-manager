from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import csv

app = Flask(__name__)
DB_NAME = "library.db"

# --- Database init ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS authors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author_id INTEGER,
                    FOREIGN KEY (author_id) REFERENCES authors (id)
                )''')
    conn.commit()
    conn.close()

init_db()

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books')
def books():
    search = request.args.get('search', '')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if search:
        c.execute('''SELECT books.id, books.title, authors.name 
                     FROM books LEFT JOIN authors ON books.author_id = authors.id
                     WHERE books.title LIKE ? OR authors.name LIKE ?''', (f'%{search}%', f'%{search}%'))
    else:
        c.execute('''SELECT books.id, books.title, authors.name 
                     FROM books LEFT JOIN authors ON books.author_id = authors.id''')
    books = c.fetchall()
    conn.close()
    return render_template('books.html', books=books, search=search)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author_name = request.form['author_name']
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Перевіряємо чи автор вже є
        c.execute("SELECT id FROM authors WHERE name = ?", (author_name,))
        author = c.fetchone()
        
        if author:
            # Автор існує - беремо його ID
            author_id = author[0]
        else:
            # Автора немає - створюємо нового
            c.execute("INSERT INTO authors (name) VALUES (?)", (author_name,))
            author_id = c.lastrowid
        
        # Додаємо книгу
        c.execute("INSERT INTO books (title, author_id) VALUES (?, ?)", (title, author_id))
        conn.commit()
        conn.close()
        return redirect(url_for('books'))
    else:
        return render_template('add_book.html')

@app.route('/update_book/<int:book_id>', methods=['POST'])
def update_book(book_id):
    title = request.form['title']
    author_id = request.form['author_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE books SET title=?, author_id=? WHERE id=?", (title, author_id, book_id))
    conn.commit()
    conn.close()
    return redirect(url_for('books'))

@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('books'))

@app.route('/authors')
def authors():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM authors")
    authors = c.fetchall()
    conn.close()
    return render_template('authors.html', authors=authors)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO authors (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return redirect(url_for('books'))
    else:
        return render_template('add_author.html')

@app.route('/delete_author/<int:author_id>')
def delete_author(author_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE author_id=?", (author_id,))
    c.execute("DELETE FROM authors WHERE id=?", (author_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('authors'))

@app.route('/export')
def export_books():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT books.title, authors.name 
                 FROM books LEFT JOIN authors ON books.author_id = authors.id''')
    rows = c.fetchall()
    conn.close()
    with open("books_export.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Author"])
        writer.writerows(rows)
    return send_file("books_export.csv", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)