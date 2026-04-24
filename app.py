from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

DB_NAME = "bookstore.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@app.route("/")
def home():
    conn = get_db_connection()
    categories = conn.execute("""
        SELECT categoryId, categoryName, categoryImage
        FROM category
        ORDER BY categoryId
    """).fetchall()
    conn.close()

    return render_template("home.html", categories=categories)


@app.route("/category/<int:category_id>")
def category_page(category_id):
    conn = get_db_connection()

    category = conn.execute("""
        SELECT categoryId, categoryName, categoryImage
        FROM category
        WHERE categoryId = ?
    """, (category_id,)).fetchone()

    books = conn.execute("""
        SELECT bookId, title, author, isbn, price, image, readNow
        FROM book
        WHERE categoryId = ?
        ORDER BY title
    """, (category_id,)).fetchall()

    conn.close()

    return render_template("category.html", category=category, books=books)


@app.route("/search", methods=["POST"])
def search():
    keyword = request.form["search"].strip()

    conn = get_db_connection()
    books = conn.execute("""
        SELECT bookId, title, author, price, image
        FROM book
        WHERE title LIKE ?
        ORDER BY title
    """, (f"%{keyword}%",)).fetchall()
    conn.close()

    return render_template("search_results.html", books=books, keyword=keyword)


@app.route("/author", methods=["POST"])
def author_search():
    keyword = request.form["author"].strip()

    conn = get_db_connection()
    books = conn.execute("""
        SELECT bookId, title, author, price, image
        FROM book
        WHERE author LIKE ?
        ORDER BY author, title
    """, (f"%{keyword}%",)).fetchall()
    conn.close()

    return render_template("author_results.html", books=books, keyword=keyword)


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    conn = get_db_connection()

    book = conn.execute("""
        SELECT book.bookId, book.title, book.author, book.isbn, book.price,
               book.image, book.readNow, category.categoryName
        FROM book
        JOIN category ON book.categoryId = category.categoryId
        WHERE book.bookId = ?
    """, (book_id,)).fetchone()

    conn.close()

    return render_template("book_detail.html", book=book)


if __name__ == "__main__":
    app.run(debug=True)
