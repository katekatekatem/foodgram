from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    """Фильтрация рецептов по тегам."""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def is_favorited_filter(self, queryset, _, value):
        user = self.request.user
        if value and not user.is_anonymous:
            queryset = queryset.filter(recipe__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, _, value):
        user = self.request.user
        if value and not user.is_anonymous:
            queryset = queryset.filter(recipe_to_buy__user_to_buy=user)
        return queryset


class IngredientFilter(filters.FilterSet):
    """Фильтрация ингредиентов."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
