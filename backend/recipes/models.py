from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

User = get_user_model()


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(max_length=settings.NAME_LENGTH)
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField('Tag', through='RecipeTag')
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:settings.STR_LENGTH]


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(max_length=settings.NAME_LENGTH)
    slug = models.SlugField(
        max_length=settings.TAG_SLUG_LENGTH,
        unique=True,
    )
    color = models.CharField(
        max_length=settings.TAG_COLOR_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:settings.STR_LENGTH]


class RecipeTag(models.Model):
    """Связующая модель рецептов и тегов."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=settings.NAME_LENGTH)
    measurement_unit = models.CharField(
        max_length=settings.NAME_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:settings.STR_LENGTH]


class RecipeIngredient(models.Model):
    """Связующая модель рецептов и ингредиентов."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f'{self.recipe} {self.ingredient} {self.amount}'
