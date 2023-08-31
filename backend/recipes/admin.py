from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import (Ingredient, Favorite, Recipe, RecipeIngredient,
                     RecipeTag, Shopping_cart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'author',
        'pub_date',
        'is_favorited_sum',
    ]
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = (RecipeTagInline, RecipeIngredientInline)

    def is_favorited_sum(self, request):
        current_recipe_is_favorited = Favorite.objects.filter(
            recipe__id=request.id)
        is_favorited_sum = len(current_recipe_is_favorited)
        return is_favorited_sum


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'amount']
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'color']
    empty_value_display = '-пусто-'


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'tag']
    list_filter = ('tag',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    empty_value_display = '-пусто-'


@admin.register(Shopping_cart)
class Shopping_cartAdmin(admin.ModelAdmin):
    list_display = ['user_to_buy', 'recipe_to_buy']
    empty_value_display = '-пусто-'


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
