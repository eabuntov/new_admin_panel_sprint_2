from django.urls import path

from .views import FilmWorkListApi, FilmWorkDetailApi

urlpatterns = [
    path('movies/', FilmWorkListApi.as_view()),
    path('movies/<pk>', FilmWorkDetailApi.as_view())
]
