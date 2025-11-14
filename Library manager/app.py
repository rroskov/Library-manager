from flask import Flask, render_template, request, redirect, url_for, send_file
import csv

app = Flask(__name__)

# Список книг у пам'яті (замінює базу даних)
books = []
book_id = 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books')
def books_page():
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    global book_id
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        books.append({
            'id': book_id,
            'title': title,
            'author': author,
            'genre': genre
        })
        book_id += 1
        return redirect(url_for('books_page'))
    return render_template('add_book.html')

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    for book in books:
        if book['id'] == id:
            if request.method == 'POST':
                book['title'] = request.form['title']
                book['author'] = request.form['author']
                book['genre'] = request.form['genre']
                return redirect(url_for('books_page'))
            return render_template('add_book.html', book=book, edit=True)
    return redirect(url_for('books_page'))

@app.route('/delete_book/<int:id>')
def delete_book(id):
    global books
    books = [b for b in books if b['id'] != id]
    return redirect(url_for('books_page'))

@app.route('/export')
def export_books():
    with open("books_export.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Book Name", "Author Name", "Genre"])
        for b in books:
            writer.writerow([b['title'], b['author'], b['genre']])
    return send_file("books_export.csv", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
