
import os

from urlparse import urlparse
from peewee import PostgresqlDatabase

from flask import Flask
app = Flask(__name__)

DEBUG = True
SECRET_KEY = os.urandom(32)

db_params = urlparse(os.environ.get('DATABASE_URL',"postgres://localhost/paulc"))

db = PostgresqlDatabase(database=db_params.path[1:],
                        user=db_params.username,
                        password=db_params.password,
                        host=db_params.hostname,
                        port=db_params.port)
db.connect()

@app.route('/')
def hello():
    return db.execute('select version()').fetchone()[0]

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
