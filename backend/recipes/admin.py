from django.contrib import admin

from .models import (Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        # 'is_favorited_sum',
    )
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = (RecipeTagInline, RecipeIngredientInline)

    # def is_favorited_sum(self, request):
    #     current_recipe_is_favorited = Recipe.objects.filter(
    #         recipe__id=request.id).values_list('is_favorited', flat=True)
    #     total_amount = sum(current_recipe_is_favorited)
    #     return total_amount


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    empty_value_display = '-пусто-'
