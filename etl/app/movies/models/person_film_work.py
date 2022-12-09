from django.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import UUIDMixin


class PersonRoleChoices(models.TextChoices):
    actor = 'actor', _('actor')
    director = 'director', _('director')
    writer = 'writer', _('writer')


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField(_('role'), choices=PersonRoleChoices.choices, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'],
                                    name='film_work_person_role_uniq')
        ]
        indexes = [
            models.Index(fields=['film_work', 'person', 'role'],
                         name='film_work_person_role_idx')
        ]
        verbose_name = 'Актер фильма'
        verbose_name_plural = 'Актеры фильма'
