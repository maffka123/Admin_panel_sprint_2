from django.urls import path

from api.v1 import views

urlpatterns = [
    path('movies/', views.MoviesListAll.as_view()),
    path('movies/<uuid:pk>/', views.MoviesDetailApi.as_view())
]