
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

c = db.cursor()

