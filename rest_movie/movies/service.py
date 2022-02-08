from django_filters import rest_framework as filters
from movies.models import Movie


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


# указывает поля и доп логику с помощью которой мы будем фильтровать
class MovieFilter(filters.FilterSet):
    # field_name - поле по которому мы должны искать. lookup_expr - указываем
    # как нужно фильтровать
    genres = CharFilterInFilter(field_name='genres__name', lookup_expr='in')
    year = filters.RangeFilter()

    class Meta:
        model = Movie
        fields = ['genres', 'year']
