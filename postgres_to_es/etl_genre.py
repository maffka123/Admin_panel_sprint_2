import pandas as pd

from etl import BaseETL
from utils import coroutine, get_env, get_logger, id_list

logger = get_logger()


class GenreETL(BaseETL):
    """
    Class for etl process, which moves data from postgres DB to elasticsearch
    """

    @coroutine
    def extract_first_level_connections(self, data):
        """
        Coroutine that queries postgres to get genres based on the movies ids gotten in the previous step
        :param data:
        :return: dataframe with genres data + movies
        """
        while True:
            logger.info('extracting movies from postgres')
            df = (yield)
            if not df.empty:
                genres_ids = id_list(df['id'])
                query = f"""
                        SELECT movie_id, array_agg(name) as genre
                        FROM genre
                        JOIN (SELECT * FROM film_work_genre WHERE genre_id in ({genres_ids})) film_work_genre
                        ON film_work_genre.genre_id = genre.id
                        GROUP BY movie_id
                        """
                df = pd.read_sql_query(query, self.psql)
                logger.info('extracted %s movies from postgres' % str(len(df)))
            data.send(df)

    @coroutine
    def extract_second_level_connections(self, data):
        """
        Coroutine that queries postgres to get people based on the moves ids gotten in the previous step,
        and enrich movies data
        :param data:
        :return: dataframe with movies data + genres + person
        """
        while True:
            logger.info('extracting person from postgres')
            df = (yield)
            if not df.empty:
                movie_ids = id_list(df['id'])
                query = f'''
                        WITH movies_person AS (SELECT movie_id, role, array_agg(name) as person
                        FROM person
                        JOIN (SELECT * FROM film_work_person WHERE movie_id in ({movie_ids})) film_work_person
                        ON film_work_person.person_id = person.id
                        GROUP BY movie_id, role)
                        SELECT * FROM film_work
                        JOIN movies_person ON film_work.id = movies_person.movie_id
                        '''
                df = pd.read_sql_query(query, self.psql)
                # split people by their role: movie_id | role | name -> movie_id | directors | actors | writers
                people = df.pivot(index='movie_id', columns='role', values='person').reset_index()
                logger.info('extracted %s persons from postgres' % str(len(people)))
                df = df.merge(people, on='movie_id', how='left').drop(columns=['movie_id', 'person', 'role'])
            data.send(df)


if __name__ == '__main__':
    get_env()
    etl_genre = GenreETL('genre')
    etl_genre.run_etl()
