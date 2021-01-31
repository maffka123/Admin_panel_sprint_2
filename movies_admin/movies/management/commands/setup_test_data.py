from django.db import transaction
from django.core.management.base import BaseCommand
from sqlalchemy import create_engine
import sqlalchemy

#from movies.models import Genre, FilmWork, Person, FilmWorkPerson, FilmWorkGenre
from movies.factories import (FilmWorkTestFactory, GenreTestFactory, PersonTestFactory)

def random_match(engine):
    """
    randomly matches id between filmwork, genre and series into intermediate table.
    I found thats easier than all djangos perverted logic
    :param engine: sqlchemy engine connection to db
    :return: None
    """

    query = """
    INSERT into content.film_work_person(movie_id, person_id, created_on)
    SELECT id as movie_id, 
    (SELECT id FROM content.person TABLESAMPLE BERNOULLI (50) LIMIT 1) as person_id,
    CURRENT_TIMESTAMP as created_on
    FROM content.film_work TABLESAMPLE BERNOULLI (10) LIMIT 1;
        INSERT into content.film_work_genre(movie_id, genre_id, created_on)
    SELECT id as movie_id, 
    (SELECT id FROM content.genre TABLESAMPLE BERNOULLI (50) LIMIT 1) as genre_id,
    CURRENT_TIMESTAMP as created_on
    FROM content.film_work TABLESAMPLE BERNOULLI (10) LIMIT 1;
    """
    for _ in range(100000):
        try:
            engine.execute(query)
        except sqlalchemy.exc.IntegrityError:
            pass

def setup_indexes(engine):
    """
    This function sets up indexes in the tables
    :param engine: sqlchemy engine connection to db
    :return:  None
    """
    query = """
    CREATE INDEX movies_idx ON content.film_work(title);
    CREATE INDEX person_idx ON content.person(name);
    CREATE INDEX genre_idx ON content.genre(name);
    CREATE INDEX film_work_person_idx ON content.film_work_person(movie_id, person_id);
    CREATE INDEX film_work_genre_idx ON content.film_work_genre(movie_id, genre_id);
    """

    engine.execute(query)


class Command(BaseCommand):
    help = "Generates test data"

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            #self.stdout.write("Deleting old data...")
            #models = [Genre, FilmWork, Person, FilmWorkPerson, FilmWorkGenre]
            #for m in models:
            #    m.objects.all().delete()

            self.stdout.write("Creating new data...")
            # Create all the movies
            self.stdout.write("Creating movies")
            for _ in range(100000):
                FilmWorkTestFactory()

            # Create all the genres
            self.stdout.write("genres")
            for _ in range(10000):
                GenreTestFactory()

            # Create all the people
            self.stdout.write("people")
            for _ in range(10000):
                PersonTestFactory()

        self.stdout.write("matching the data")
        engine = create_engine('postgresql://postgres:vfifif@localhost:5432/movies_database')
        random_match(engine)
        self.stdout.write("Setting up indexes")
        setup_indexes(engine)


