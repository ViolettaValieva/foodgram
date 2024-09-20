from django.utils.crypto import get_random_string

from core.constants import SHORT_URL_LENGTH


def generate_short_url(model):
    """Генерация уникальной короткой ссылки для рецепта."""
    while True:
        short_url = get_random_string(SHORT_URL_LENGTH)
        if not model.objects.filter(short_url=short_url).exists():
            return short_url
