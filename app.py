
import os,sys

from urlparse import urlparse
import psycopg2
from flask import Flask,abort,request

#DEBUG = os.environ.get('DEBUG',False)
DEBUG = True
SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config.from_object(__name__)

db_params = urlparse(os.environ.get('DATABASE_URL'))

db = psycopg2.connect(database=db_params.path[1:],
                      user=db_params.username,
                      password=db_params.password,
                      host=db_params.hostname,
                      port=db_params.port)

db.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

class cursor(object):
    def __init__(self,db):
        self.db = db
    def __enter__(self):
        self.c = db.cursor()
        return self.c
    def __exit__(self,type,value,traceback):
        self.c.close()

def text(msg,code=200):
    return (msg,code,{'Content-type':'text/plain'})

@app.route('/')
def root():
    return text("LiveAuth")

@app.route('/ping')
def ping():
    with cursor(db) as c:
        c.execute('select version()')
        return text(c.fetchone()[0])

@app.route('/list')
def list():
    with cursor(db) as c:
        c.execute('SELECT state,code,inserted FROM token ORDER by inserted')
        rows = []
        for row in c:
            rows.append("%s : %s (%s)" % row)
        return text("\n".join(rows))

@app.route('/callback')
def callback():
    with cursor(db) as c:
        state = request.values['state']
        code = request.values['code']
        c.execute('INSERT into token(state,code) values (%s,%s)',(state,code))
        return text("State: %s\nCode:  %s" % (state,code))

@app.route('/get/<state>')
def get(state):
    with cursor(db) as c:
        c.execute("SELECT code FROM token WHERE state = %s",(state,))
        try:
            token, = c.fetchone()
            return text(token)
        except TypeError, e:
            return text("Key not found",404)

@app.route('/delete')
@app.route('/delete/<int:secs>')
def drop(secs=0):
    with cursor(db) as c:
        c.execute("DELETE FROM token WHERE extract('epoch' from now() - inserted) > %s",(secs,));
        return text("%d rows deleted" % c.rowcount)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
