#!/bin/bash

# copied from here: https://stackoverflow.com/questions/29600369/starting-and-populating-a-postgres-container-in-docker
# this script is run when the docker container is built
# it imports the base database structure and create the database for the tests

DATABASE_NAME="movies_database"

echo "*** CREATING DATABASE ***"

cp ./psql.dump /var/lib/postgresql/data/pgdata/psql.dump

# import sql_dump
createdb $DATABASE_NAME -U postgres
psql -U postgres -d $DATABASE_NAME -c "GRANT ALL PRIVILEGES ON DATABASE "$DATABASE_NAME" TO postgres;"
psql  -U postgres  -d movies_database < /var/lib/postgresql/data/pgdata/psql.dump


echo "*** DATABASE CREATED! ***"