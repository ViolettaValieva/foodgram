from django.shortcuts import get_object_or_404, redirect

from .models import Recipe


def redirect_to_original(request, slug):
    """Перенаправление с короткой ссылки на оригинальную."""
    recipe = get_object_or_404(Recipe, short_url=slug)
    return redirect(f'/recipes/{recipe.pk}/')
