import sqlite3
from flask import Flask, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS news
        (id INTEGER PRIMARY KEY,
         date TEXT,
         text TEXT,
         author TEXT)
    ''')
    # Clear existing data
    c.execute('DELETE FROM news')
    
    news_data = [
        (1, datetime.datetime.now().isoformat(), "The quick brown fox jumps over the lazy dog.", "John Doe"),
        (2, datetime.datetime.now().isoformat(), "Never underestimate the power of a good book.", "Jane Smith"),
        (3, datetime.datetime.now().isoformat(), "Technology is a double-edged sword.", "Peter Jones"),
        (4, datetime.datetime.now().isoformat(), "The early bird catches the worm.", "Mary Williams"),
        (5, datetime.datetime.now().isoformat(), "Actions speak louder than words.", "David Brown"),
        (6, datetime.datetime.now().isoformat(), "A picture is worth a thousand words.", "Susan Davis"),
        (7, datetime.datetime.now().isoformat(), "The pen is mightier than the sword.", "Robert Miller"),
        (8, datetime.datetime.now().isoformat(), "When in Rome, do as the Romans do.", "Linda Wilson"),
        (9, datetime.datetime.now().isoformat(), "The squeaky wheel gets the grease.", "Michael Moore"),
        (10, datetime.datetime.now().isoformat(), "No man is an island.", "Patricia Taylor"),
        (11, datetime.datetime.now().isoformat(), "Fortune favors the bold.", "Charles Anderson"),
        (12, datetime.datetime.now().isoformat(), "Hope for the best, but prepare for the worst.", "Barbara Thomas"),
        (13, datetime.datetime.now().isoformat(), "Better late than never.", "James Jackson"),
        (14, datetime.datetime.now().isoformat(), "Birds of a feather flock together.", "Jennifer White"),
        (15, datetime.datetime.now().isoformat(), "Keep your friends close and your enemies closer.", "Richard Harris")
    ]
    
    c.executemany('INSERT INTO news VALUES (?,?,?,?)', news_data)
    conn.commit()
    conn.close()

@app.route('/news')
def get_news():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('SELECT * FROM news ORDER BY date DESC')
    news = [{'id': row[0], 'date': row[1], 'text': row[2], 'author': row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(news)

if __name__ == '__main__':
    init_db()
    app.run(port=5001)
