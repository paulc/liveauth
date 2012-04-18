
import os

from urlparse import urlparse
from peewee import PostgresqlDatabase
from flask import Flask,request

DEBUG = os.environ.get('DEBUG',False)
SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config.from_object(__name__)

db_params = urlparse(os.environ.get('DATABASE_URL'))

db = PostgresqlDatabase(database=db_params.path[1:],
                        user=db_params.username,
                        password=db_params.password,
                        host=db_params.hostname,
                        port=db_params.port)
db.connect()

@app.route('/')
def version():
    return (db.execute('select version()').fetchone()[0],200,{'Content-type':'text/plain'})

@app.route('/oauth')
def oauth():
    r = []
    for k,v in request.values.iteritems():
        r.append("Key: %s / Value: %s" % (k,v)) 
    return ("\n".join(r),200,{'Content-type':'text/plain'})

@app.route('/error')
def error():
    raise Exception("An error")

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
