"""
ETL process for updating ES base in case if film_work table in postgres will be changed
"""
import abc
import os
import time

import backoff
import pandas as pd
from sqlalchemy import create_engine

from es_operations import ES
from state_tracking import BaseStorage, State
from utils import coroutine, get_logger

logger = get_logger()


class BaseETL:
    """
    Base ETL class that defines all steps needed for an etl pipeline to move data from postgers to elasticsearch
    """
    def __init__(self, table):
        self.es = ES()
        engine_data = os.environ.get('postgres')
        self.psql = create_engine(engine_data, connect_args={'options': '-csearch_path=content'})
        self.table = table
        bs = BaseStorage(self.table)
        self.state = State(bs)

    @backoff.on_exception(backoff.expo, Exception, max_tries=10)
    def run_etl(self):
        """
        Runs full ETL pipeline
        :return: None
        """
        l = self.load_to_es()
        t = self.transform_sql_to_es(l)
        e3 = self.extract_second_level_connections(t)
        e2 = self.extract_first_level_connections(e3)
        self.extract_changed_table_from_psql(e2)

    # здесь не нужен декоратор, ну в примере его не было и всё рабоает без него
    # https://praktikum.yandex.ru/learn/middle-python/courses/af061b15-1607-45f2-8d34-f88d4b21765a/sprints/5030/topics/665ba0d6-6eab-41d5-84dd-bbc1997930fb/lessons/0e75f376-4a12-422e-8fa3-64e3ef5904e5/
    def extract_changed_table_from_psql(self, data):
        """
        Coroutine that queries postgres to get changed table, that was updated after updated_at time written in state
        :param data:
        :return: dataframe with tables data
        """
        while True:
            logger.info('extracting %s from postgres' % self.table)
            time.sleep(6)
            updated_at = self.state.get_state()
            query = f"""
            SELECT * FROM {self.table} 
            WHERE updated_at > '{updated_at}'
            ORDER by updated_at
            LIMIT 100
            """
            df = pd.read_sql_query(query, self.psql)
            logger.info('extracted %s %s from postgres' % (str(len(df)), self.table))
            data.send(df)

    @abc.abstractmethod
    def extract_first_level_connections(self, data):
        """
        Extract tables most closely connected to the changed table
        :return: joined df with previous and new data
        """
        pass

    @abc.abstractmethod
    def extract_second_level_connections(self, data):
        """
        Extract rest tables
        :return: joined df with previous and new data
        """
        pass

    @coroutine
    def transform_sql_to_es(self, data):
        """
        Coroutine that prepares data for sending to elasticsearch, makes list with dictionaries
        from each row of the table
        :param data:
        :return: list with dictionaries and the date of the last updated movies, for state update
        """
        while True:
            logger.info('preparing data for elasticserach')
            df = (yield)
            docs = []
            updated_at = self.state.get_state()  # just because with df it is easier
            if not df.empty:
                updated_at = max(df['updated_at']).strftime(format='%Y-%m-%d %H:%M:%S.%f')
                for i, row in df.iterrows():
                    # drop columns with no values
                    row = row.dropna()
                    row = row[row != '']
                    row = row[row != 'N/A']
                    # convert the rest to dict
                    doc = row.to_dict()
                    docs.append(doc)
            data.send([docs, updated_at])

    @coroutine
    def load_to_es(self):
        """
        Coroutine that sends data to elasticsearch
        :return: None
        """
        while True:
            logger.info('sending data to elasticsearch')
            data = (yield)
            self.es.bulk_load_data('movies', data[0])
            self.state.set_state(data[1])  # update state after all is done
