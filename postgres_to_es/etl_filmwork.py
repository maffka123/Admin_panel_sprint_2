"""
ETL process for updating ES base in case if film_work table in postgres will be changed
"""
import logging
from functools import wraps
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import pandas as pd
import time
import backoff

from state_tracking import State, BaseStorage
from es_operations import ES

basedir = os.getcwd()
if os.path.isfile(f'{basedir}/../src/.env'):
    load_dotenv(dotenv_path=f'{basedir}/../src/.env')
else:
    load_dotenv(dotenv_path=f'{basedir}/src/.env')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
engine_data = os.environ.get('postgres')


class ETL:
    """
    Class for etl process, which moves data from postgres DB to elasticsearch
    """

    @backoff.on_exception(backoff.expo, Exception, max_tries=10)
    def __init__(self):
        self.es = ES()
        self.psql = create_engine(engine_data, connect_args={'options': '-csearch_path=content'})
        self.bs = BaseStorage()
        self.state = State(self.bs)
        l = self.load_to_es()
        t = self.transform_sql_to_es(l)
        e3 = self.extract_people_from_psql(t)
        e2 = self.extract_genres_from_psql(e3)
        e1 = self.extract_movies_from_psql(e2)

    def coroutine(func):
        """
        wraps coroutine function to avoid their initialisation with none and using next
        see: https://medium.com/@chandansingh_99754/python-generators-and-coroutines-d54ed9c343ae
        see: https://praktikum.yandex.ru/learn/middle-python/courses/af061b15-1607-45f2-8d34-f88d4b21765a/sprints/5030/topics/665ba0d6-6eab-41d5-84dd-bbc1997930fb/lessons/0e75f376-4a12-422e-8fa3-64e3ef5904e5/
        :return: next
        """

        @wraps(func)
        def inner(*args, **kwargs):
            fn = func(*args, **kwargs)
            next(fn)
            return fn

        return inner

    def extract_movies_from_psql(self, data):
        """
        Coroutine that queries postgres to get movies that were updated after updated_at time in written in state
        :param data:
        :return: dataframe with movies data
        """
        while True:
            logger.info('extracting movies from postgres')
            time.sleep(6)  # TODO: something smarter, there is a way to track if postgres was updated
            updated_at = self.state.get_state('film_work')
            query = f"""
            SELECT * FROM film_work 
            WHERE updated_at > '{updated_at}'
            ORDER by updated_at
            LIMIT 100
            """
            df = pd.read_sql_query(query, self.psql)
            logger.info('extracted %s movies from postgres' % str(len(df)))
            data.send(df)

    @coroutine
    def extract_genres_from_psql(self, data):
        """
        Coroutine that queries postgres to get genres based on the moves ids gotten in the previous step
        :param data:
        :return: dataframe with movies data + genres
        """
        while True:
            logger.info('extracting genres from postgres')
            df = (yield)
            if not df.empty:
                movie_ids = df['id'].unique()
                movie_ids = ', '.join("'"+str(id)+"'" for id in movie_ids)
                query = f"""
                    SELECT movie_id, array_agg(name) as genre
                    FROM genre
                    JOIN (SELECT * FROM film_work_genre WHERE movie_id in ({movie_ids})) film_work_genre
                    ON film_work_genre.genre_id = genre.id
                    GROUP BY movie_id
                    """
                genre = pd.read_sql_query(query, self.psql)
                logger.info('extracted %s genres from postgres' % str(len(genre)))
                df = df.merge(genre, left_on='id', right_on='movie_id', how='left').drop(columns=['movie_id'])
            data.send(df)

    @coroutine
    def extract_people_from_psql(self, data):
        """
        Coroutine that queries postgres to get people based on the moves ids gotten in the previous step
        :param data:
        :return: dataframe with movies data + genres + people
        """
        while True:
            logger.info('extracting people from postgres')
            df = (yield)
            if not df.empty:
                movie_ids = df['id'].unique()
                movie_ids = ', '.join("'" + str(id) + "'" for id in movie_ids)
                query = f'''
                    SELECT movie_id, role, array_agg(name) as name
                    FROM person
                    JOIN (SELECT * FROM film_work_person WHERE movie_id in ({movie_ids})) film_work_person
                    ON film_work_person.person_id = person.id
                    GROUP BY movie_id, role
                    '''
                people = pd.read_sql_query(query, self.psql)
                # split people by their role: movie_id | role | name -> movie_id | directors | actors | writers
                people = people.pivot(index='movie_id', columns='role', values='name').reset_index()
                logger.info('extracted %s persons from postgres' % str(len(people)))
                df = df.merge(people, left_on='id', right_on='movie_id', how='left').drop(columns=['movie_id'])
            data.send(df)

    @coroutine
    def transform_sql_to_es(self, data):
        """
        Coroutine that prepares data for sending to elasticsearch, makes list with dictionaries from each row of the table
        :param data:
        :return: list with dictionaries and the date of the last updated movies, for state update
        """
        while True:
            logger.info('preparing data for elasticserach')
            df = (yield)
            docs = []
            updated_at = self.state.get_state('film_work') # just because with df it is easier
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
        :param data:
        :return: None
        """
        while True:
            logger.info('sending data to elasticsearch')
            data = (yield)
            self.es.bulk_load_data('movies', data[0])
            self.state.set_state('film_work', data[1]) # update state after all is done

if __name__ == '__main__':
    etl = ETL()