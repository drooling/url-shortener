import secrets
import sqlite3

from flask import (Flask, abort, jsonify, redirect, render_template, request,
                   url_for)

app = Flask(__name__)

@app.before_first_request
def before_first_request():
    global database
    global cursor

    database = sqlite3.connect("urls.db", check_same_thread=False)
    cursor = database.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS `urls` (
            `long_url` TEXT NOT NULL,
            `code` TEXT NOT NULL
        );""")
    database.commit()

@app.route('/', methods=["GET"])
def index():
    return render_template('index.html')

@app.route('/create', methods=["POST"])
def create():
    long_url = request.form.get('long_url', False)
    if not long_url:
        abort(400)
    cursor.execute("SELECT code FROM `urls` WHERE long_url=?;", (long_url,))
    existing_record = (cursor.fetchone() or False)
    if existing_record:
        return jsonify({"long_url": str(long_url), "code": str(existing_record[0])})
    code = secrets.token_urlsafe(6)
    cursor.execute("INSERT INTO `urls` (long_url, code) VALUES (?, ?);", (long_url, code))
    database.commit()
    return jsonify({"long_url": str(long_url), "code": str(code)})

@app.route('/<code>', methods=["GET"])
def use_short_url(code):
    cursor.execute("SELECT long_url FROM `urls` WHERE code=?;", (code,))
    try:
        return redirect(cursor.fetchone()[0])
    except TypeError:
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)
