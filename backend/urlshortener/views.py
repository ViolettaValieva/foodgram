from django.shortcuts import get_object_or_404, redirect

from .models import ShortURL


def redirect_to_original(request, short_url):
    """Перенаправление с короткой ссылки на оригинальную."""
    short_url_instance = get_object_or_404(ShortURL, short_url=short_url)
    return redirect(short_url_instance.original_url)
