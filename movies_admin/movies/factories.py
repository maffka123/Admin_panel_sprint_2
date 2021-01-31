import factory
from factory.django import DjangoModelFactory
from datetime import datetime

from .models import Genre, FilmWork, Person, FilmWorkPerson, FilmWorkGenre
import random


class GenreTestFactory(DjangoModelFactory):
    class Meta:
        model = Genre

    id = factory.Faker('uuid4')
    name = factory.Faker("sentence", nb_words=1)

class PersonTestFactory(DjangoModelFactory):
    class Meta:
        model = Person

    id = factory.Faker('uuid4')
    name = factory.Faker("sentence", nb_words=1)
    role = factory.LazyFunction(lambda: random.choice(['actor', 'writer', 'director']))

# Defining a factory
class FilmWorkTestFactory(DjangoModelFactory):
    class Meta:
        model = FilmWork

    id = factory.Faker('uuid4')
    title = factory.Faker("company")
    plot = factory.Faker("sentence", nb_words=10, variable_nb_words=True)
    ratings = factory.LazyFunction(lambda: random.choice([x for x in range(10)]))
    video_type = factory.LazyFunction(lambda: random.choice(['series', 'movie']))


class FilmWorkPersoTestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FilmWorkPerson

    movie_id = factory.SubFactory(FilmWorkTestFactory)
    person_id = factory.SubFactory(PersonTestFactory)

class FilmWorkPersoTestFactory2(FilmWorkTestFactory):
    membership = factory.RelatedFactory(
        FilmWorkPersoTestFactory,
        factory_related_name='movie_id',
    )

class FilmWorkGenreTestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FilmWorkGenre

    movie_id = factory.SubFactory(FilmWorkTestFactory)
    genre_id = factory.SubFactory(GenreTestFactory)

class FilmWorkGenreTestFactory2(FilmWorkTestFactory):
    membership = factory.RelatedFactory(
        FilmWorkGenreTestFactory,
        factory_related_name='movie_id',
    )
