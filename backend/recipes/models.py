from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

from foodgram_backend.constants import (MAX_AMOUNT, MAX_COOKING_TIME, MIN,
                                        NAME_LENGTH, STR_LENGTH,
                                        TAG_SLUG_LENGTH)
from users.models import CustomUser


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(max_length=NAME_LENGTH)
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField('Tag', through='RecipeTag')
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'text'],
                name='name&text',
            )
        ]

    def __str__(self):
        return self.name[:STR_LENGTH]


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(max_length=NAME_LENGTH)
    slug = models.SlugField(
        max_length=TAG_SLUG_LENGTH,
        unique=True,
    )
    color = ColorField()

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:STR_LENGTH]


class RecipeTag(models.Model):
    """Связующая модель рецептов и тегов."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Рецепты и теги'
        verbose_name_plural = 'Рецепты и теги'

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=NAME_LENGTH)
    measurement_unit = models.CharField(
        max_length=NAME_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name&measurement_unit',
            )
        ]

    def __str__(self):
        return self.name[:STR_LENGTH]


class RecipeIngredient(models.Model):
    """Связующая модель рецептов и ингредиентов."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN), MaxValueValidator(MAX_AMOUNT)]
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Рецепты и ингредиенты'
        verbose_name_plural = 'Рецепты и ингредиенты'

    def __str__(self):
        return f'{self.recipe} {self.ingredient} {self.amount}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
    )

    class Meta:
        ordering = ('user__username',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user&recipe',
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user}, рецепт {self.recipe}'


class Shopping_cart(models.Model):
    """Модель списка покупок."""

    user_to_buy = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user_to_buy',
    )
    recipe_to_buy = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_to_buy',
    )

    class Meta:
        ordering = ('user_to_buy__username',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            UniqueConstraint(
                fields=['user_to_buy', 'recipe_to_buy'],
                name='unique_user_to_buy&recipe_to_buy',
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user_to_buy}, рецепт {self.recipe_to_buy}'
