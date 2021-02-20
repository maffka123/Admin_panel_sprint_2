import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine

from utils import get_env, get_logger

logger = get_logger()
get_env()


@dataclass
class BaseStorage:

    table_name: str

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
            # because we don't want to run 3 times the same stuff at the start of the ETL,
            # get different times for tables
            which_time_to_get = {'film_work': 'min', 'genre': 'max', 'person': 'max'}
            for table in which_time_to_get:
                date = psql.execute(f'SELECT {which_time_to_get[table]}(updated_at) FROM {table};').fetchall()[0][0]
                tables_states[table] = date.strftime(format='%Y-%m-%d %H:%M:%S')

            with open('state.dump', 'w') as f:
                json.dump(tables_states, f)
        else:
            logger.info('CHECK: dump file exists, working with it')

    def save_state(self, updated_at: str) -> None:
        """
        Saves key:value of a state. All states are in one file if form: table_name: updated_at
        If file with state does not exist it creates it with a new dictionary.
        If file exists, adds or updates states info
        :param updated_at: when it was updated
        :return: None
        """
        logger.info('CHECK: %s updates at %s' % (self.table_name, updated_at))
        with open('state.dump', 'r') as f:
            tables_states = json.load(f)

        tables_states[self.table_name] = updated_at  # add/updated value for particular table

        with open('state.dump', 'w') as f:
            json.dump(tables_states, f)

    def retrieve_state(self) -> dict:
        """
        retrives datetime at which load process stopped last time
        :return: str with datetime of process stop
        """
        logger.info('CHECK: getting updates for %s' % self.table_name)
        with open('state.dump', 'r') as f:
            state = json.load(f)

        return state[self.table_name]


@dataclass
class State:
    """
    Class to store state a which ETL process is now
    """
    storage: BaseStorage

    def set_state(self, updated_at: str) -> None:
        self.storage.save_state(updated_at)

    def get_state(self) -> Any:
        return self.storage.retrieve_state()
