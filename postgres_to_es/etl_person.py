import pandas as pd

from etl import BaseETL
from utils import coroutine, get_env, get_logger, id_list

logger = get_logger()


class PersonETL(BaseETL):
    """
    Class for etl process, which moves data from postgres DB to elasticsearch
    """

    @coroutine
    def extract_first_level_connections(self, data):
        """
        Coroutine that queries postgres to get movies based on the person ids gotten in the previous step
        :param data:
        :return: dataframe with person data + movies
        """
        while True:
            logger.info('extracting movies from postgres')
            df = (yield)
            if not df.empty:
                person_ids = id_list(df['id'])
                query = f"""
                       SELECT movie_id, array_agg(name) as name, role
                       FROM person
                       JOIN (SELECT * FROM film_work_person WHERE person_id in ({person_ids})) film_work_person
                       ON film_work_person.person_id = person.id
                       GROUP BY movie_id, role
                       """
                df = pd.read_sql_query(query, self.psql)
                logger.info('extracted %s movies from postgres' % str(len(df)))
                # split people by their role: movie_id | role | name -> movie_id | directors | actors | writers
                df = df.pivot(index='movie_id', columns='role', values='name').reset_index()
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
                           WITH movies_genre AS (SELECT movie_id, array_agg(name) as genre
                           FROM genre
                           JOIN (SELECT * FROM film_work_genre WHERE movie_id in ({movie_ids})) film_work_genre
                           ON film_work_genre.genre_id = genre.id
                           GROUP BY movie_id)
                           SELECT * FROM film_work
                           JOIN movies_genre ON film_work.id = movies_genre.movie_id
                           '''
                genres = pd.read_sql_query(query, self.psql)
                logger.info('extracted %s genres from postgres' % str(len(genres)))
                df = df.merge(genres, on='movie_id', how='left').drop(columns=['movie_id'])
            data.send(df)


if __name__ == '__main__':
    get_env()
    etl_person = PersonETL('person')
    etl_person.run_etl()
