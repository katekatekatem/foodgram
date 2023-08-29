from django_filters import rest_framework as filters

from recipes.models import Ingredient, Favorite, Recipe, Shopping_cart, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтрация рецептов по тегам."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            is_favorited = Favorite.objects.filter(user=user)
            recipes = [item.recipe.id for item in is_favorited]
            queryset = queryset.filter(id__in=recipes)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            is_in_shopping_cart = Shopping_cart.objects.filter(
                user_to_buy=user
            )
            recipes = [item.recipe_to_buy.id for item in is_in_shopping_cart]
            queryset = queryset.filter(id__in=recipes)
        return queryset


class IngredientFilter(filters.FilterSet):
    """Фильтрация ингредиентов."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
