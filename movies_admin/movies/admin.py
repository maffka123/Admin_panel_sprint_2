from django.contrib import admin
from .models import FilmWork, Actor, Writer, Director, Person, Movie, Series
from django import forms


class GenreInlineAdmin(admin.TabularInline):
    model = FilmWork.genre.through

class PersonInlineAdmin(admin.TabularInline):
    model = Person.movie.through


class SeparatePersonsForm(forms.ModelForm):

    actor = Person.objects.filter(role='actor')
    writer = Person.objects.filter(role='writer')
    director = Person.objects.filter(role='director')
    actors = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple, queryset=actor, required=False)
    writers = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple, queryset=writer, required=False)
    directors = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple, queryset=director, required=False)

    class Meta:
        model = FilmWork
        fields = '__all__'


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):

    # отображение полей в списке
    list_display = ('title', 'ratings', 'updated_at', 'actors', 'writers', 'director',
                    'film_creation_date', 'age_limit', 'link')
    def actors(self, obj):
        actors = FilmWork.objects.filter(people__role__iexact='actor', title=obj).values_list('people__name', flat=True)
        return ", ".join([a for a in actors])
    def writers(self, obj):
        writers = FilmWork.objects.filter(people__role__iexact='writer', title=obj).values_list('people__name', flat=True)
        return ", ".join([a for a in writers])
    def director(self, obj):
        director = FilmWork.objects.filter(people__role__iexact='director', title=obj).values_list('people__name', flat=True)
        return ", ".join([a for a in director])


    # фильтрация в списке
    list_filter = ('genre', 'film_creation_date', 'age_limit', 'link')
    form = SeparatePersonsForm
    fieldsets = (
        (None, {
            'fields': ('title', 'plot', 'ratings', 'film_creation_date', 'age_limit', 'link', 'actors', 'writers', 'directors'),
        }),
    )

    # поиск по полям
    search_fields = ('title', 'plot', 'id', 'film_creation_date', 'age_limit', 'link')

    inlines = (GenreInlineAdmin, )

    #autocomplete_fields = ['actor']

    def save_model(self, request, obj, form, change):
        obj.save()
        q1 = form.cleaned_data.get('actors', None)
        q2 = form.cleaned_data.get('writers', None)
        q3 = form.cleaned_data.get('directors', None)
        q1 = q1.union(q2).union(q3)
        obj.person_set.set(q1)



@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):

    # отображение полей в списке
    list_display = ('name', )

    # порядок следования полей в форме создания/редактирования
    fields = ('name', )

    # поиск по полям
    search_fields = ('name', )

    # фильтрация в списке
    list_filter = ('movie',)

    inlines = (PersonInlineAdmin,)


@admin.register(Writer)
class WriterAdmin(admin.ModelAdmin):

    # отображение полей в списке
    list_display = ('name',)

    # порядок следования полей в форме создания/редактирования
    fields = ('name',)

    # поиск по полям
    search_fields = ('name',)

    # фильтрация в списке
    list_filter = ('movie', )

    inlines = (PersonInlineAdmin,)

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):

    # отображение полей в списке
    list_display = ('name',)

    # порядок следования полей в форме создания/редактирования
    fields = ('name',)

    # поиск по полям
    search_fields = ('name', )

    # фильтрация в списке
    list_filter = ('movie',)

    inlines = (PersonInlineAdmin,)



@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):

    def actors(self, obj):
        actors = Series.objects.filter(people__role__iexact='actor', title=obj).values_list('people__name', flat=True)
        return ", ".join([a for a in actors])
    def writers(self, obj):
        writers = Series.objects.filter(people__role__iexact='writer', title=obj).values_list('people__name', flat=True)
        return ", ".join([a for a in writers])
    def director(self, obj):
        director = Series.objects.filter(people__role__iexact='director', title=obj).values_list('people__name', flat=True)
        return ", ".join([a for a in director])

    # отображение полей в списке
    list_display = ('title', 'ratings', 'updated_at','actors', 'writers', 'director',
                    'film_creation_date', 'link')


    # фильтрация в списке
    list_filter = ('genre', 'film_creation_date', 'link')

    form = SeparatePersonsForm
    fieldsets = (
        (None, {
            'fields': ('title', 'plot', 'ratings', 'film_creation_date', 'link', 'actors', 'writers', 'directors'),
        }),
    )

    # поиск по полям
    search_fields = ('title', 'plot', 'id', 'film_creation_date', 'link')

    inlines = (GenreInlineAdmin, )

    def save_model(self, request, obj, form, change):
        obj.save()
        q1 = form.cleaned_data.get('actors', None)
        q2 = form.cleaned_data.get('writers', None)
        q3 = form.cleaned_data.get('directors', None)
        q1 = q1.union(q2).union(q3)
        obj.person_set.set(q1)

