from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag
from users.models import CustomUser

from . import serializers
from .filters import RecipeFilter
from .mixins import ListRetriveCreateDestroyViewSet
from .permissions import (IsAdminOrReadOnlyPermission, IsAdminPermission,
                          IsAdminOrAuthorOrReadOnlyPermission)


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserRegistrationSerializer
        return serializers.CustomUserSerializer

    def get_permissions(self):
        if self.action == 'create' or self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else: 
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(
        ['GET'],
        url_path='me',
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        if request.method == 'GET':
            return Response(
                serializers.CustomUserSerializer(request.user).data,
                status=status.HTTP_200_OK,
            )


class IngredientViewSet(ListRetriveCreateDestroyViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class TagViewSet(ListRetriveCreateDestroyViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnlyPermission,)
    http_method_names = ['get', 'post', 'put', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT'):
            return serializers.RecipeCreateSerializer
        return serializers.RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class Download_shopping_cartViewSet(viewsets.ModelViewSet):
    ...


class Shopping_cartViewSet(viewsets.ModelViewSet):
    ...


class FavoriteViewSet(viewsets.ModelViewSet):
    ...


class SubscriptionsViewSet(viewsets.ModelViewSet):
    ...


class SubscribeViewSet(viewsets.ModelViewSet):
    ...
