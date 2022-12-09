from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .genre import Genre
from .mixins import TimeStampedMixin, UUIDMixin
from .person import Person


class FilmTypes(models.TextChoices):
    movie = 'movie', _('movie')
    tv_show = 'tv_show', _('tv_show')


class Filmwork(TimeStampedMixin, UUIDMixin):
    certificate = models.CharField(_('certificate'), max_length=512, blank=True, null=True, default='')
    # Параметр upload_to указывает, в какой подпапке будут храниться загружемые файлы.
    # Базовая папка указана в файле настроек как MEDIA_ROOT
    file_path = models.FileField(_('file'), blank=True, null=True,
                                 upload_to='movies/')
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateTimeField(_('creation_date'), auto_now_add=True, null=True)
    rating = models.FloatField(_('rating'), null=True, blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])
    type = models.CharField(_('type'),
                            max_length=100, default='movie',
                            choices=FilmTypes.choices)

    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"film_work"
        indexes = [
            models.Index(fields=['creation_date'], name='film_work_creation_date_idx'),
            models.Index(fields=['title'], name='film_work_title_idx')
        ]
        verbose_name = _('filmwork')
        verbose_name_plural = _('filmworks')
