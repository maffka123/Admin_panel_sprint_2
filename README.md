# Admin panel for online cinema packed into docker

The panel is build according to the followitn schema:

![all](images/all.png)


## To start the service from docker:

``docker-compose up -d``

<span style="color:red">Attention! It was testet only on Mac, make sure that Docker has permissions for the folder,
where you run it</span>

for details see: https://stackoverflow.com/questions/58482352/operation-not-permitted-from-docker-container-logged-as-root


## To start the panel by yourself from the mysql dump you need to do the following:

* install requirements.txt in your python environment

* create environment variable ```postgres``` with connection data,
e.g. ```postgresql://user:pass@localhost:5432/movies_database```

* start postgres from docker (this is suggestion for mac):

```bash
sudo docker run -d --rm \
  --name postgres \
  -p 5432:5432 \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v .:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=vfifif \
  postgres:13
```

* Migrate sqlite db to this postgres:

    * Create schema:
    ```bash
    docker exec -it postgres psql -U postgres
    ```

    and the copypaste content of ya_postgres_schema.psql

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

![Alt text](admin_panel.png?raw=true "Optional Title")

