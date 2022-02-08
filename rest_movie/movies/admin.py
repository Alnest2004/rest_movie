from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from .models import *
from ckeditor_uploader.widgets import CKEditorUploadingWidget



class MovieAdminForm(forms.ModelForm):
    """Форма с виджетом ckeditor"""

    # _ru _en - Добавляем их, так как мы используем ckeditor.
    description = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())

    class Meta:
        model = Movie
        fields = '__all__'



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Категории"""
    # list_display указывает какие поля отображать на странице списка объектов.
    list_display = ("id", "name", "url")
    list_display_links = ("name",)
    prepopulated_fields = {"url": ("name",)}

# При открытии записи нашего фильма мы видели все отзывы, которые прикреплены к данному
# фильму, это делает данный класс.
# Если вы хотите редактировать и добавлять объекты Image на странице
# добавления/редактирования объектов Product, вы можете использовать GenericStackedInline
"""
class StackedInline(выводит в строках) и TabularInline(выводит в столбцах)
Интерфейс администратора позволяет редактировать связанные объекты на одной
странице с родительским объектом. Это называется “inlines”. Например, у нас есть
две модели:
"""
class ReviewInLine(admin.TabularInline):
    """Отзывы на странице фильма"""
    model = Review
    # Указывает количество дополнительных полей
    extra = 1
    # указываем поля которые будут только для чтения
    readonly_fields = ("name", "email")


# Выводим те данные которые привязаны к данной модели MovieShots
class MovieShotsInLine(admin.TabularInline):
    model = MovieShots
    extra = 1
    readonly_fields = ("get_image", )
    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} width="100" height="110" ')

    get_image.short_description = "Изображение"


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Фильмы"""
    list_display = ("title", "category", "url", "draft")
    list_filter = ("category", "year")
    search_fields = ("title", "category__name")
    # Интерфейс администратора позволяет редактировать связанные объекты на одной
    # странице с родительским объектом. Это называется “inlines”
    inlines = [MovieShotsInLine, ReviewInLine]
    save_on_top = True
    # Если save_as равен True, “Сохранить и добавить новый” будет заменена кнопкой
    # “Сохранить как”. Укажите save_as, чтобы включить возможность “сохранять как”
    # на странице редактирования объекта.
    save_as = True
    # указываем поле которое можем редактировать не заходя в него
    list_editable = ("draft", )
    # тут мы добавляем в действия функции, которые прописали ниже.
    actions = ["publish", "unpublish"]
    form = MovieAdminForm
    readonly_fields = ("get_image", )
    # объединяем данные поля в один. В кортеже указываем кортеж полей, которые должны
    # быть в одной строке
    # fields = (("actors", "directors", "genres"), )
    # указываем кортеж который будет содержать кортежи содержать словарь, где
    # мы указываем ключ fields и кортеж тех полей которых мы хотим использовать
    # если мы указываем двойной кортеж, значит мы объединяем в одну строку эти поля
    fieldsets = (
        (None, {
            "fields": (("title", "tagline"), )
        }),
        (None, {
            "fields": ("description", ("poster", "get_image"))
        }),
        (None, {
            "fields": (("year", "world_premiere", "country"), )
        }),
        ("Актёры", {
            # указываем ключ classes и значением передаём кортеж с именем класса collapse
            # тем самым делаем данную вкладку свёрнутой. Группа полей с классом collapse
            # будет показа в свернутом виде с кнопкой “развернуть”.
            # classes - Список содержащий CSS классы, которые будут добавлены в группу полей."""
            "classes": ("collapse ", ),
            "fields": (("actors", "directors", "genres", "category"), )
        }),
        (None, {
            "fields": (("budget", "fess_in_usa", "fess_in_world"), )
        }),
        ("Options", {
            "fields": (("url", "draft"),)
        }),
    )

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.poster.url} width="100" height="110" ')

    # QuerySet, по сути, — список объектов заданной модели. QuerySet
    # позволяет читать данные из базы данных, фильтровать и изменять их порядок.
    def unpublish(self, request, queryset):
        """Снять с публикации"""
        # тут мы снимаем с публикации выбранные элементы
        row_update = queryset.update(draft=True)
        # Далее проверяем сколько записей было обновлено
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        # тут мы выводим сообщение в админку после обновления
        self.message_user(request, f"{message_bit}")

    def publish(self, request, queryset):
        """Опубликовать"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        self.message_user(request, f"{message_bit}")

    publish.short_description = "Опубликовать"
    publish.allowed_permissions = {'change', }

    unpublish.short_description = "Снять с публикации"
    unpublish.allowed_permissions = {'change', }

    get_image.short_description = "Изображение"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Отзывы"""
    list_display = ("name", "email", "parent", "movie", "id")
    # поля только для чтения(то есть нельзя редактировать)
    readonly_fields = ("name", "email")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Жанры"""
    list_display = ("name", "url")



@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    """Актёры"""
    list_display = ("name", "age", "get_image")
    readonly_fields = ("get_image", )

    # принимает модель объекта актёров
    def get_image(self, obj):
        # mark_safe - выведет html не как строку, а как тег
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} width="50" height="60" ')

    get_image.short_description = "Изображение"


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Рейтинг"""
    list_display = ("star", "movie", "ip")


@admin.register(MovieShots)
class MovieShotsAdmin(admin.ModelAdmin):
    """Кадры из фильма"""
    list_display = ("title", "movie", "get_image")
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} width="50" height="60" ')

    get_image.short_description = "Изображение"

# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Genre)
# admin.site.register(Movie)
# admin.site.register(MovieShots)
# admin.site.register(Actor)
# admin.site.register(Rating)
admin.site.register(RatingStar)
# admin.site.register(Reviews)

admin.site.site_title = "Django Movies"
admin.site.site_header = "Django Movies"

