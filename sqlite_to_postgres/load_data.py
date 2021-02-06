import sqlite3
from sqlalchemy import create_engine
from sqlalchemy import engine as _engine

from sqlite_to_postgres.utils.sqlite_loader import read_db
from sqlite_to_postgres.utils.pg_schema_converter import df_to_pg

from datetime import datetime

from dotenv import load_dotenv
import os
load_dotenv()

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

table_names = ['film_work', 'genre', 'person', 'film_work_genre', 'film_work_person']


def load_from_sqlite(connection: sqlite3.Connection, engine: _engine):
    """
    orchestration
    :return: None
    """

    # read and assemble all date from sqlite to one df
    all_data = read_db(connection)
    logger.info('all data: done %s rows', len(all_data))

    # prepare several dfs for export to postgres
    film_work, genre, person, film_work_genre, film_work_person = df_to_pg(all_data)
    logger.info('data converted: done')

    # send tables to postgres
    for i, table in enumerate([film_work, genre, person, film_work_genre, film_work_person]):
        table['created_on'] = datetime.now()
        table.to_sql(table_names[i], engine, if_exists='append', index=False, schema='content') # for load in batches: chunksize

    logger.info('Tables inserted to postgresql: done')


if __name__ == '__main__':
    engine_data = os.environ.get("postgres")
    engine = create_engine(engine_data)
    with sqlite3.connect('db.sqlite') as sqlite_conn:
        load_from_sqlite(sqlite_conn, engine)

