
import os,sys
from urlparse import urlparse
from flask import Flask,abort,request

import db

DEBUG = os.environ.get('DEBUG',False)
SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config.from_object(__name__)

def text(msg,code=200):
    return (msg,code,{'Content-type':'text/plain'})

@app.route('/')
def root():
    return text("LiveAuth")

@app.route('/ping')
def ping():
    with db.cursor() as c:
        c.execute('select version()')
        return text(c.fetchone()[0])

@app.route('/list')
def list():
    with db.cursor() as c:
        c.execute('SELECT state,code,error,error_description,inserted FROM token ORDER by inserted')
        rows = []
        for state,code,error,error_description,inserted in c:
            if error:
                rows.append("%s : ERROR %s (%s) [%s]" % (state,error,error_description,inserted))
            else:
                rows.append("%s : %s [%s]" % (state,code,inserted))
        return text("\n".join(rows))

@app.route('/callback')
def callback():
    with db.cursor() as c:
        state = request.values['state']
        if request.values.has_key('error'):
            error = request.values['error']
            error_description = request.values['error_description']
            c.execute('INSERT into token(state,error,error_description) values (%s,%s,%s)',
                                        (state,error,error_description))
            return text("State: %s\nError: (%s) %s" % (state,error,error_description))
        else:
            code = request.values['code']
            c.execute('INSERT into token(state,code) values (%s,%s)',(state,code))
            return text("State: %s\nCode:  %s" % (state,code))

@app.route('/get/<state>')
def get(state):
    with db.cursor() as c:
        c.execute("SELECT code,error,error_description FROM token WHERE state = %s",(state,))
        try:
            token,error,error_description = c.fetchone()
            if error:
                return text("ERROR: %s (%s)" % (error,error_description))
            else:
                return text("%s" % token)
        except TypeError, e:
            return text("Key not found",404)

@app.route('/delete')
@app.route('/delete/<int:secs>')
def drop(secs=0):
    with db.cursor() as c:
        c.execute("DELETE FROM token WHERE extract('epoch' from now() - inserted) > %s",(secs,));
        return text("%d rows deleted" % c.rowcount)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
