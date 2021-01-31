from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.http import Http404
from django.core.paginator import InvalidPage
from django.utils.translation import gettext_lazy as _

from movies.models import FilmWork

class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        """
        creates QuerySet with all data from film_work table including m2m fields genre and people split by their role
        :return: QuerySet
        """
        id = self.request.GET.get('id')
        print(id)
        if id == None:
            all_movies = FilmWork.objects.prefetch_related(
                                        'Genre', 'Person').values().annotate(
                                        genres=ArrayAgg('genre__name'),
                                        actors=ArrayAgg('people__name', filter=Q(people__role='actor')),
                                        directors=ArrayAgg('people__name', filter=Q(people__role='director')),
                                        writers=ArrayAgg('people__name', filter=Q(people__role='writer')))
        else:
            all_movies = FilmWork.objects.filter(id=id).prefetch_related(
                                        'genre', 'people').annotate(
                                        genres=ArrayAgg('genre__name'),
                                        actors=ArrayAgg('people__name', filter=Q(people__role='actor')),
                                        directors=ArrayAgg('people__name', filter=Q(people__role='director')),
                                        writers=ArrayAgg('people__name', filter=Q(people__role='writer')))

        return all_movies


class MoviesListAll(MoviesApiMixin, BaseListView):
    model = FilmWork
    http_method_names = ['get']  # Список методов, которые реализует обработчик
    paginate_by = 50

    def get_queryset(self):
        """
        creates QuerySet with all data from film_work table including m2m fields genre and people split by their role
        :return: QuerySet
        """

        all_movies = FilmWork.objects.prefetch_related(
                                    'genre', 'people').values().annotate(
                                    genres=ArrayAgg('genre__name'),
                                    actors=ArrayAgg('people__name', filter=Q(people__role='actor')),
                                    directors=ArrayAgg('people__name', filter=Q(people__role='director')),
                                    writers=ArrayAgg('people__name', filter=Q(people__role='writer')))

        return all_movies

    def paginate_queryset(self, queryset, page_size):
        """Paginate the queryset, if needed."""
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())

        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_('Page is not “last”, nor can it be converted to an int.'))
        try:
            page = paginator.page(page_number)
            count = paginator.count
            total_pages = paginator.num_pages
            prev = page.previous_page_number() if page.has_previous() else None
            next = page.next_page_number() if page.has_next() else None
            return (page.object_list, count, total_pages, prev, next)
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset, count, total_pages, prev, next = self.paginate_queryset(self.get_queryset(), page_size=self.paginate_by)
        print('-------------------')
        print(queryset)
        context = {
            'count': count,
            'total_pages': total_pages,
            'prev': prev,
            'next': next,
            'results': list(queryset)
        }
        return context


    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False)


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_queryset(self):
        """
        creates QuerySet with data corresponding to film id from film_work table including m2m fields genre and
        people split by their role
        :return: QuerySet
        """
        all_movies = FilmWork.objects.filter(id=self.kwargs['pk']).prefetch_related(
                                    'Genre', 'Person').values().annotate(
                                    genres=ArrayAgg('genre__name'),
                                    actors=ArrayAgg('people__name', filter=Q(people__role='actor')),
                                    directors=ArrayAgg('people__name', filter=Q(people__role='director')),
                                    writers=ArrayAgg('people__name', filter=Q(people__role='writer')))

        return all_movies

    def get_context_data(self, **kwargs):
        context = {
            'results': list(self.get_queryset()),
        }
        return  context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)