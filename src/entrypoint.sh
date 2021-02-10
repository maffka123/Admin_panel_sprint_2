#!/bin/bash

echo "yes\n" | movies_admin/manage.py collectstatic

# Just because admin needs to wait until db is built
result=$(python <<EOF
from sqlalchemy import create_engine
import time
engine = create_engine('postgresql://postgres:vfifif@postgres:5432/movies_database')
tries = 5
while tries != 0:
    try:
        rows = engine.execute('SELECT * FROM content.genre LIMIT 1')
        tries = 0
    except:
        time.sleep(10)
        tries -=1
EOF
)
cd movies_admin
gunicorn --bind 0.0.0.0:8000 config.wsgi
#./manage.py runserver # use for debugging, gunicorn does not print all logs