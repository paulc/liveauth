
import os,select,time
import psycopg2
from urlparse import urlparse

db_params = urlparse(os.environ.get('DATABASE_URL','postgres://localhost/paulc'))

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

def drop_db(db):
    with cursor(db) as c:
        c.execute('DROP TABLE token CASCADE')

def init_db(db):
    with cursor(db) as c:
        c.execute('SELECT tablename FROM pg_tables WHERE schemaname=%s and tablename=%s',
                                             ('public','token'));
        if c.fetchone() != ('token',):
            c.execute('''CREATE TABLE token (state TEXT PRIMARY KEY,
                                             appname TEXT NOT NULL,
                                             code TEXT NOT NULL,
                                             inserted TIMESTAMP NOT NULL DEFAULT NOW())''')

c = db.cursor()

