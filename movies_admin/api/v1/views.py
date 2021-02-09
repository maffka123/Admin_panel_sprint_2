from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView


from movies.models import FilmWork

class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        """
        creates QuerySet with all data from film_work table including m2m fields genre and people split by their role
        :return: QuerySet
        """

        all_movies = FilmWork.objects.prefetch_related(
                                        'Genre', 'Person').annotate(
                                        genres=ArrayAgg('genre__name'),
                                        actors=ArrayAgg('people__name', filter=Q(people__role='actor')),
                                        directors=ArrayAgg('people__name', filter=Q(people__role='director')),
                                        writers=ArrayAgg('people__name', filter=Q(people__role='writer')))

        return all_movies.values()

    def render_to_response(self, context, **response_kwargs):

        return JsonResponse(context, safe=False)


class MoviesListAll(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):

        all_data = self.get_queryset()
        paginator, page, object_list, is_paginated = self.paginate_queryset(all_data, self.paginate_by)
        count = paginator.count
        total_pages = paginator.num_pages
        prev = page.previous_page_number() if page.has_previous() else None
        next = page.next_page_number() if page.has_next() else None

        context = {
            'count': count,
            'total_pages': total_pages,
            'prev': prev,
            'next': next,
            'results': list(object_list)
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):

        one_data = self.get_queryset().filter(id=self.kwargs['pk'])
        context = {
            'results': one_data,
        }

        return context

