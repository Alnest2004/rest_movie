from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from django.db import models
from .models import Movie, Actor
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    ReviewCreateSerializer,
    CreateRatingSerializer,
    ActorListSerializer,
    ActorDetailSerializer,
)
from .service import get_client_ip, MovieFilter


class MovieListView(generics.ListAPIView):
    """Вывод списка фильмов"""
    serializer_class = MovieListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MovieFilter

    # Будет срабатывать при get запросе
    def get_queryset(self):
        # Подсчитываем количество установленных рейтингов пользователям нашему фильму
        # так как пользователь может установить только 1 раз рейтинг к фильму
        # и если такая запись будет найдена вернётся 1, если нет то 0.
        # ratings - Это related_name модели rating. Добавляем фильтр где поле
        # ip рейтинга будет равно ip нашего пользователя.
        # annotate по идеи добавляет ещё одно поле для вывода значения
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        return movies


class MovieDetailView(generics.RetrieveAPIView):
    """Вывод фильма"""
    queryset = Movie.objects.filter(draft=False)
    serializer_class = MovieDetailSerializer



class ReviewCreateView(generics.CreateAPIView):
    """Добавление отзыва к фильму"""
    # data=request.data - данные которые содержатся в нашем клиентском запросе
    serializer_class = ReviewCreateSerializer



class AddStarRatingView(generics.CreateAPIView):
    """Добавление рейтинга фильму"""

    serializer_class = CreateRatingSerializer

    # принимает сериализацию и в метод save указываем параметры которые
    # дополнительно хотим сохранить
    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


class ActorsListView(generics.ListAPIView):
    """Вывод списка актёров"""
    queryset = Actor.objects.all()
    serializer_class = ActorListSerializer

#RetrieveAPIView - для вывода полного описания, аналог detailview
class ActorsDetailView(generics.RetrieveAPIView):
    """Вывод актёра или режиссёра"""
    queryset = Actor.objects.all()
    serializer_class = ActorDetailSerializer
