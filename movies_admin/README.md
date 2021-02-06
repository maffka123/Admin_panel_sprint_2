# Admin panel for online-cinema

## To start the panel you need to do the following steps:

* install requirements.txt in your python environment

* create environment variable ```postgres``` with connection data,
e.g. ```postgresql://user:pass@localhost:5432/movies_database```

* start postgres from docker (this is suggestion for mac):

```bash
sudo docker run -d --rm \
  --name postgres \
  -p 5432:5432 \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v /Users/maria/Desktop/ya_mid_level_dev/ya_proj/Admin_panel_sprint_1:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=vfifif \
  postgres:13
```

* Migrate sqlite db to this postgres:

    * Create schema:
    ```bash
    docker exec -it postgres bash
    psql -U postgres
    ```

    and the copypaste content of schema_design/ya_postgres_schema.psql

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





