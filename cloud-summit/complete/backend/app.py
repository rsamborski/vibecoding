from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

def get_db_connection():
    conn = sqlite3.connect('news.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/news')
def get_news():
    conn = get_db_connection()
    news_items = conn.execute('SELECT * FROM news ORDER BY date DESC, id DESC').fetchall()
    conn.close()
    # Convert row objects to dictionaries
    news_list = [dict(ix) for ix in news_items]
    return jsonify(news_list)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
