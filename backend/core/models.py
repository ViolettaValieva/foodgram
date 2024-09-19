from django.conf import settings
from django.db import models


class UserRecipeModel(models.Model):
    """Абстрактная модель для связи пользователя с рецептом."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)ss'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s'
            ),
        )

    def __str__(self):
        return f'{self._meta.verbose_name} - {self.recipe.name}'
