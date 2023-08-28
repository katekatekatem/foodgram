from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('users', views.UserViewSet, basename='users')
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')
router.register('tags', views.TagViewSet, basename='tags')

registration_urls = [
    path(
        'users/set_password/',
        UserViewSet.as_view({'post': 'set_password'}),
        name='set_password',
    ),
]

urlpatterns = [
    path('', include(registration_urls)),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
