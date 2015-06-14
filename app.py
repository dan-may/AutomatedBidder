"""
This script runs the web server that listens for GET requests in the format:
HTTP 1.1 GET /keyword-performance/{keyword}?start_date={start_date}&end_date={end_date}
"""
import sys
import sqlite3
import statistics
import string
from flask import Flask, request, jsonify, g, abort

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

DATABASE = 'adwords.db'

def connect_to_database():
    return sqlite3.connect(DATABASE)

# The following three functions taken from Flask best practise on database querying
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def hello():
    """Renders a sample page."""
    return "Hello LogicNow!"

@app.route('/keyword-performance/<string:keyword>')
def keyword_performance(keyword):
    """Gets keyword data"""
    keyword = keyword.replace('"', '').replace("'", '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    if start_date == '' or end_date == '':
        abort(400)   

    keyword_id = query_db('select * from keywords where keyword_text = ?',
                (keyword,), one=True)
    if keyword_id is None:
        abort(400)
    
    data = []
    for row in query_db('select * from keyword_performance where keyword_id = ? and date between ? and ?', 
                        (keyword_id['keyword_id'], start_date, end_date)):
        revenue = str.strip(row['revenue'], '$')
        data.append(float(revenue))
       
    rpc = statistics.mean(data)
    std = statistics.stdev(data)

    return jsonify(rpc = rpc, std = std)

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)