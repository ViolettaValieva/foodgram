from django.db import models
from django.utils.crypto import get_random_string

from core.constants import (SHORT_URL_LENGTH, SHORT_URL_MAX_LENGTH,
                            URL_MAX_LENGTH)


class ShortURL(models.Model):
    """Модель коротких ссылок."""

    original_url = models.URLField(max_length=URL_MAX_LENGTH)
    short_url = models.CharField(max_length=SHORT_URL_MAX_LENGTH,
                                 unique=True)

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = get_random_string(SHORT_URL_LENGTH)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return f'{self.short_url} -> {self.original_url}'
