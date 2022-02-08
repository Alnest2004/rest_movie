from django.core.cache import cache
from .models import Category

class DataMixin:

    def get_user_context(self, **kwargs):
        context = kwargs
        cats = Category.objects.all()
        context['categories'] = cats
        return context