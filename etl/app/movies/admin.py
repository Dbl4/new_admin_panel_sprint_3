from django.contrib import admin

from .models.filmwork import Filmwork
from .models.genre import Genre
from .models.genre_film_work import GenreFilmwork
from .models.person import Person
from .models.person_film_work import PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):

    list_display = ('name', 'description',)

    search_fields = ('name', 'description', 'id')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):

    list_display = ('full_name',)

    search_fields = ('full_name', 'id')


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    # Отображение полей в списке
    list_display = ('title', 'type', 'creation_date', 'rating',)

    # Фильтрация в списке
    list_filter = ('type',)

    # Поиск по полям
    search_fields = ('title', 'description', 'id')