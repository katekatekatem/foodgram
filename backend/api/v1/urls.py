from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


router_v1 = DefaultRouter()
router_v1.register('users', views.UserViewSet, basename='users')
router_v1.register(
    'users/subscriptions',
    views.SubscriptionsViewSet,
    basename='subscriptions'
)
router_v1.register(
    r'users/(?P<user_id>\d+)/subscribe',
    views.SubscribeViewSet,
    basename='subscribe'
)
router_v1.register('recipes', views.RecipeViewSet, basename='recipes')
router_v1.register(
    'recipes/download_shopping_cart',
    views.Download_shopping_cartViewSet,
    basename='download_shopping_cart'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    views.Shopping_cartViewSet,
    basename='shopping_cart'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    views.FavoriteViewSet,
    basename='favorite'
)
router_v1.register(
    'ingredients',
    views.IngredientViewSet,
    basename='ingredients'
)
router_v1.register('tags', views.TagViewSet, basename='tags')


registration_uls = [
    path('signup/', views.SignUpView.as_view()),
    path('token/', views.GetTokenView.as_view()),
]


urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include(registration_uls)),
]
