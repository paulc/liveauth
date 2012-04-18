
import os,sys

from urlparse import urlparse
import psycopg2
from flask import Flask,request

DEBUG = os.environ.get('DEBUG',False)
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

def init_db(db):
    with cursor(db) as c:
        c.execute('SELECT tablename FROM pg_tables WHERE schemaname=%s and tablename=%s',
                                             ('public','token'));
        if c.fetchone() != ('token',):
            c.execute('''CREATE TABLE token (state TEXT PRIMARY KEY,
                                             code TEXT NOT NULL,
                                             inserted TIMESTAMP NOT NULL DEFAULT NOW())''')

init_db(db)

@app.route('/')
def root():
    return "LiveAuth"

@app.route('/ping')
def ping():
    with cursor(db) as c:
        c.execute('select version()')
        return c.fetchone()[0]

@app.route('/oauth')
def oauth():
    with cursor(db) as c:
        state = request.values['state']
        code = request.values['code']
        c.execute('INSERT into token(state,code) values (%s,%s)',(state,code))
        return ("State: %s\nCode:  %s\n" % (state,code),200,{'Content-type':'text/plain'})

@app.route('/list')
def list():
    with cursor(db) as c:
        c.execute('SELECT * FROM token')
        rows = []
        for row in c:
            rows.append("%s : %s (%s)" % row)
        return "<html><body><pre>%s</pre></body></html>" % "<br>".join(rows)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
