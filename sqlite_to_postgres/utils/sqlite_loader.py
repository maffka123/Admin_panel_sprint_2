import pandas as pd
import logging
import ast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_db(conn):
    """
    read movies joined with actors and read separate writers. Then add writers names to mvoe table
    to have all data in one table
    TODO: could be nice to have some verification that everything was read correctly, and fix in case of error
    :param conn: connection object to db
    :return: dataframe with all writers
    """
    # read movies from db, joined with actor names
    query = '''
    WITH actor_name AS 
      (SELECT movie_id, name AS actors_names
        FROM 
        ---remove duplicates from movie_actors 
        (SELECT DISTINCT * FROM movie_actors) ma
        LEFT JOIN 
        ---remove non-valid N/A from actors
        (SELECT DISTINCT * FROM actors WHERE name!="N/A") a
        ON ma.actor_id=a.id)
    SELECT DISTINCT * FROM
    movies 
    LEFT JOIN actor_name
    ON movies.id=actor_name.movie_id'''

    # TODO: i'm not sure, but there are about 70 duplicates, which need smarter cleansing (see movie "Afghan Star"
    # TODO: for example), i'm not sure if it was meant like this

    logger.info('reading movies')
    movies = pd.read_sql_query(query, conn)

    # put actors into a list
    movies['actors_names'] = movies['actors_names'].apply(lambda x: '' if x is None else x)
    movies = movies.groupby('id').agg({'genre': 'first', 'director': 'first',
                                       'writer': 'first', 'title': 'first',
                                       'plot': 'first', 'ratings': 'first',
                                       'imdb_rating': 'first', 'writers': 'first',
                                       'actors_names': ', '.join}).reset_index()

    logger.info('reading writers')
    writers = pd.read_sql_query('SELECT DISTINCT * FROM writers WHERE name!="N/A"', conn)

    all_data = add_writer_names(movies, writers)
    all_data['imdb_rating'] = all_data['imdb_rating'].astype(float)

    return all_data


def add_writer_names(movies, writers):
    """
    combines movies and writers tables, so movies will have writers names and not ids/lists of ids
    :param movies: df with all infos about mvoies from sqlite
    :param writers: df with writers names and ids
    :return: combined df
    """
    logger.info('combining movies and writers')

    movies['writers_names'] = None
    for i, row in movies.iterrows():
        if row['writer'] == '': # if name is not one
            names = ast.literal_eval(row['writers']) # get list from str with writers
            names = [l["id"] for l in names] # get list of ids from list of dicts
            names = ', '.join(writers[writers['id'].isin(names)]['name'].to_list()) # get names based on ids
            movies['writers_names'].iloc[i] = names
        else: # if there is just one name
            if writers[writers['id']==row['writer']]['name'].values.size != 0:
                movies['writers_names'].iloc[i] = writers[writers['id'] == row['writer']]['name'].values[0]

    movies = movies.drop(columns=['writer', 'writers'])
    movies = movies.replace({'N/A': None})

    return movies