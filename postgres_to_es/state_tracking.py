from typing import Any
import json
import os
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger()
load_dotenv()

class BaseStorage:
    def __init__(self):
        self.get_initial_data()

    def get_initial_data(self):
        """
        If not yet exist creates dump file with initial update dates in psql
        :return: None
        """
        if not Path('state.dump').exists():
            logger.info('CHECK: dump file does not exist, creating a new one')
            engine_data = os.environ.get("postgres")

            psql = create_engine(engine_data, connect_args={'options': '-csearch_path=content'})
            tables_states = {}
            which_time_to_get = {'film_work': 'min', 'genre': 'max', 'person': 'max'} # because we don't want to run 3 times the same stuff at the start of the ETL
            for table in which_time_to_get:
                date = psql.execute(f'SELECT {which_time_to_get[table]}(updated_at) FROM {table};').fetchall()[0][0]
                tables_states[table] = date.strftime(format='%Y-%m-%d %H:%M:%S')

            with open('state.dump', 'w') as f:
                json.dump(tables_states, f)
        else:
            logger.info('CHECK: dump file exists, working with it')

    def save_state(self, table_name: str, updated_at: str) -> None:
        """
        Saves key:value of a state. All states are in one file if form: table_name: updated_at
        If file with state does not exist it creates it with a new dictionary.
        If file exists, adds or updates states info
        :param table_name: name of changed table
        :param updated_at: when it was updated
        :return: None
        """
        logger.info('CHECK: %s updates at %s' % (table_name, updated_at))
        with open('state.dump', 'r') as f:
            tables_states = json.load(f)

        tables_states[table_name] = updated_at # add/updated value for particular table

        with open('state.dump', 'w') as f:
            json.dump(tables_states, f)

    def retrieve_state(self, table_name) -> dict:
        logger.info('CHECK: getting updates for %s' % table_name)
        with open('state.dump', 'r') as f:
            state = json.load(f)

        return state[table_name]

class State:
    """
    Class to store state a which ETL process is now
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, table_name: str, updated_at: str) -> None:
        self.storage.save_state(table_name, updated_at)

    def get_state(self, table_name: str) -> Any:
        self.state = self.storage.retrieve_state(table_name)
        return self.state

