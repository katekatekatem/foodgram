from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """Фильтры произведений."""
    
    tag = filters.CharFilter(field_name='tag__slug')

    class Meta:
        model = Recipe
        fields = ('name', 'author', 'tag')
