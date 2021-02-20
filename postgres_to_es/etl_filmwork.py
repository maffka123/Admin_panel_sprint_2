import pandas as pd

from etl import BaseETL
from utils import coroutine, get_env, get_logger, id_list

logger = get_logger()


class FilmWorkETL(BaseETL):
    """
    Class for etl process, which moves data from postgres DB to elasticsearch
    """

    @coroutine
    def extract_first_level_connections(self, data):
        """
        Coroutine that queries postgres to get genres based on the moves ids gotten in the previous step
        :param data:
        :return: dataframe with movies data + genres
        """
        while True:
            logger.info('extracting genres from postgres')
            df = (yield)
            if not df.empty:
                movie_ids = id_list(df['id'])
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
    def extract_second_level_connections(self, data):
        """
        Coroutine that queries postgres to get people based on the moves ids gotten in the previous step
        :param data:
        :return: dataframe with movies data + genres + people
        """
        while True:
            logger.info('extracting people from postgres')
            df = (yield)
            if not df.empty:
                movie_ids = id_list(df['id'])
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


if __name__ == '__main__':
    get_env()
    etl_filmwork = FilmWorkETL('film_work')
    etl_filmwork.run_etl()
