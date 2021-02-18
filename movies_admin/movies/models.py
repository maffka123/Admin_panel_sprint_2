from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid

# --------------------Movies
class FilmWorkGenre(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    movie = models.ForeignKey('FilmWork', models.CASCADE, related_name='movie_id', unique=False)
    genre = models.ForeignKey('Genre', models.CASCADE, db_column='genre_id', unique=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'film_work_genre'
        unique_together = (('movie', 'genre'),)


class FilmWorkPerson(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    movie = models.ForeignKey('FilmWork', models.CASCADE, unique=False)
    person = models.ForeignKey('Person', models.CASCADE, unique=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'film_work_person'
        unique_together = (('movie', 'person'),)


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('название'), max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'genre'
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

    def __str__(self):
        return self.name


class FilmWork(models.Model):
    # what we have from sql
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('название'), max_length=255)
    plot = models.TextField(_('описание'), blank=True, null=True)
    ratings = models.CharField(_('рейтинг'), max_length=100, blank=True, null=True)
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    genre = models.ManyToManyField(Genre, through=FilmWorkGenre)
    people = models.ManyToManyField('Person', through=FilmWorkPerson)


    # what is also asked by ya
    film_creation_date = models.DateField(_('дата создания'),blank=True, null=True)
    age_limit = models.CharField(_('возраст'), max_length=5, blank=True, null=True)
    link = models.CharField(_('ссылка'), max_length=100, blank=True, null=True)

    # series part
    video_type = models.CharField(max_length=10, blank=True, null=True, default='movie')

    objects = models.Manager()


    class Meta:
        db_table = 'film_work'
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')

    def __str__(self):
        return self.title

class MovieManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(video_type='movie')


class Movie(FilmWork):
    objects = MovieManager()

    class Meta:
        proxy = True
        verbose_name = _('фильм')
        verbose_name_plural = _('фильмы')

    def save(self, *args, **kwargs):
        self.video_type = 'movie'
        return super(Movie, self).save(*args, **kwargs)

class SeriesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(video_type='series')


class Series(FilmWork):
    objects = SeriesManager()

    class Meta:
        proxy = True
        verbose_name = _('сериал')
        verbose_name_plural = _('сериалы')

    def save(self, *args, **kwargs):
        self.video_type = 'series'
        self.age_limit = 0
        return super(Series, self).save(*args, **kwargs)



class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=100)
    role = models.CharField(_('role'), max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    movie = models.ManyToManyField(FilmWork, through=FilmWorkPerson)

    class Meta:
        db_table = 'person'

    def __str__(self):
        return self.name


class ActorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role='actor')


class Actor(Person):
    """
    В задании есть основные сущности, среди них: Актёр — имя, фамилия, его фильмы. Режиссёр — имя, фамилия, его фильмы.
    Сценарист — имя, фамилия, его фильмы.
    Я так поняла, что должна быть возможность править их отдально (см скриншот на во внешнем readme на гитхабе)
    А ещё я столько вренемени убиоа, чтоб понять, как это сделать, что теперь я эти модели никуда не уберу 8)
    """
    objects = ActorManager()

    class Meta:
        proxy = True
        verbose_name = _('актёр')
        verbose_name_plural = _('актёры')

    def save(self, *args, **kwargs):
        self.role = 'actor'
        return super(Actor, self).save(*args, **kwargs)


class DirectorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role='actor')


class Director(Person):
    objects = DirectorManager()

    class Meta:
        proxy = True
        verbose_name = _('режисёр')
        verbose_name_plural = _('режисёры')

    def save(self, *args, **kwargs):
        self.role = 'director'
        return super(Director, self).save(*args, **kwargs)


class WriterManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role='actor')


class Writer(Person):
    objects = WriterManager()

    class Meta:
        proxy = True
        verbose_name = _('сценарист')
        verbose_name_plural = _('сценаристы')

    def save(self, *args, **kwargs):
        self.role = 'writer'
        return super(Writer, self).save(*args, **kwargs)



# -----------------Users
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    birth_date = models.DateTimeField()
