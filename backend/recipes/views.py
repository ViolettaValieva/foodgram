from django.shortcuts import get_object_or_404, redirect

from .models import Recipe


def redirect_to_original(request, short_url):
    """Перенаправление с короткой ссылки на оригинальную."""
    recipe = get_object_or_404(Recipe, short_url=short_url)
    return redirect('recipe_detail', pk=recipe.pk)
