# Admin panel for online cinema packed into docker

The panel is build according to the following schema:

![all](images/all.png)

ETL process, example for change in genres table:

![etl](images/Postgres_in_Elasticsearch.jpg)


## To start the service from docker:

You would need an .env file in src/.env, with the followingvaruables:
```
SECRET_KEY = 'verysecretkay'
PS_NAME = 'movies_database'
PS_USER ='postgres'
PS_PASSWORD = 'yourpass'
PS_HOST = 'postgres'
PS_PORT = '5432'
```

``docker-compose up -d``

wait a bit until you go to browser, there is a delay to wait until db is ready
if waiting did not help, it means that admin still started before postgres, run it all again and wait 30 s
``docker-compose down``
``docker-compose up -d``

!-------------------------------------------------------------------------------------------!

!Attention! On Mac, make sure that Docker has permissions for the folder,
where you run it!

for details see: https://stackoverflow.com/questions/58482352/operation-not-permitted-from-docker-container-logged-as-root

!-------------------------------------------------------------------------------------------!


## To start the panel by yourself from the mysql dump you need to do the following:

* install movies_admin/requirements/dev.txt in your python environment

* create environment variable ```postgres``` with connection data,
e.g. ```postgresql://user:pass@localhost:5432/movies_database```

* start postgres from docker (this is suggestion for mac):

```bash
docker run -d --rm \
  --name postgres \
  -p 5432:5432 \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v ${PWD}:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=vfifif \
  postgres:13
```

* Migrate sqlite db to this postgres:

    * Create schema:
    ```bash
    docker exec -it postgres psql -U postgres
    ```

    and the copy-paste content of ya_postgres_schema.psql

    * Migrate:
    ```bash
    python sqlite_to_postgres/load_data.py
    ```

* Change directory

```bash
cd movies_admin
```

* Make migrations:

    - Rename migrations folder to ex. .migrations
    - run ```./manage.py migrate```
    - Rename migrations back
    - ```./manage.py migrate movies 0001_initial --fake```
    - ```./manage.py migrate movies```

* Create admin:
```bash
./manage.py createsuperuser
```

* Run Django admin:
```bash
cd movies_admin
./manage.py runserver
```

* To generate random data run:
```bash
./manage.py setup_test_data
```

## The final view of the admin panel, should be like that

![Alt text](images/admin_panel.png?raw=true "Optional Title")


## Use service:

* admin panel: ``http://localhost:8000/admin/``

    user: test
    password: Thisispass1

* api: 
    - ``http://localhost:8000/api/v1/movies/`` will returrn first page with all movies
    - ``http://localhost:8000/api/v1/movies?page=2`` specify page (50 movies per page)
    - ``http://localhost:8000/api/v1/movies/01473f42-3ae0-4570-ab53-98042d655749/`` find moview by its uuid
