from rest_framework import serializers

from .models import Movie, Review, Rating, Actor


class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтр комментариев, только parents"""

    # Задача метода to_representation — представить извлечённые из записи данные в определённом виде.
    # data - это наш queryset
    def to_representation(self, data):
        # фильтруем и находим только те записи у которых нет родителя
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
    """Вывод рекурсивно children"""

    # value - Значение одной записи из бд
    def to_representation(self, value):
        # ищем всех потомков которые завязаны на нашем отзыве
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ActorListSerializer(serializers.ModelSerializer):
    """Вывод списка актёров и режиссёров"""

    class Meta:
        model = Actor
        fields = ("id", "name", "image")


class ActorDetailSerializer(serializers.ModelSerializer):
    """Вывод полного списка актёра или режиссёра"""

    class Meta:
        model = Actor
        fields = "__all__"


# Сериализаторы нужны для того что бы преобразовывать типы данных питон в
# json и обратно
class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    rating_user = serializers.BooleanField()
    middle_star = serializers.IntegerField()

    # Указываем модель и поля которые хотим сериализовать
    class Meta:
        model = Movie
        fields = ("id", "title", "tagline", "category", "rating_user", "middle_star")


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Добавление отзыва"""

    class Meta:
        model = Review
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    """Вывод отзыва"""
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Review
        fields = ("name", "text", "children")


# Сериализатор для вывода полного фильма
class MovieDetailSerializer(serializers.ModelSerializer):
    """Подробный фильм"""
    # slug_field="name" - name это поля в модели category и мы указываем
    # что бы для нашей category выводился не id, а поле name. И дальше мы
    # перебираем все поля для которых нужно вывести информацию отличную от id
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    # many = True, так как поле directors manytomany, у нас несколько таких
    # актёров или режиссёров и значит у нас будет несколько записей
    directors = ActorListSerializer(read_only=True, many=True)
    actors = ActorListSerializer(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ("draft",)


class CreateRatingSerializer(serializers.ModelSerializer):
    """Добавление рейтинга пользователя"""

    class Meta:
        model = Rating
        fields = ("star", "movie")

    def create(self, validated_data):
        # в поля ip, movie мы забираем из validated_data с помощью метода get
        # наши поля ip,movie. validated_data - Это данные которые мы передаём в
        # наш сериализатор от клиентской стороны и обновлять мы будем поле star
        # Если такой ip и movie у нас уже существует то заново создавать
        # мы не будем, а defaults будет просто перезаписывать значение(оценку)
        # мы добавили _ что бы в него записывался true или false, что бы переменная
        # rating не была кортежом. Разделив тем самых их на 2 переменные. Наш объект
        # будет передаваться в перем. rating, а в _ будет передавться true или
        # false (то есть обновилась или создалась запись)
        rating, _ = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None),
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get("star")}
        )
        return rating
