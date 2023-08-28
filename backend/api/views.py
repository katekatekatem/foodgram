from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, Shopping_cart, Tag
from users.models import CustomUser, Subscription

from . import serializers
from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetriveCreateDestroyViewSet
from .permissions import (IsAdminOrReadOnlyPermission, IsAdminPermission,
                          IsAdminOrAuthorOrReadOnlyPermission)


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer

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

    @action(
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        subscriber = self.request.user
        author = get_object_or_404(CustomUser, pk=pk)

        if self.request.method == 'POST':
            if subscriber == author:
                raise exceptions.ValidationError(
                    'Невозможно подписаться на самого себя.'
                )
            if Subscription.objects.filter(
                subscriber=subscriber,
                author=author
            ).exists():
                raise exceptions.ValidationError('Подписка уже существует.')
            Subscription.objects.create(subscriber=subscriber, author=author)
            return Response(
                serializers.SubscribeSerializer(author, context={'request': request}).data,
                status=status.HTTP_201_CREATED,
            )

        if self.request.method == 'DELETE':
            if not Subscription.objects.filter(
                subscriber=subscriber,
                author=author,
            ).exists():
                raise exceptions.ValidationError('Такой подписки не существует.')
            subscription = get_object_or_404(
                Subscription,
                subscriber=subscriber,
                author=author,
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=['GET'],
        url_path='subscriptions',
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        if request.method == 'GET':
            subscriptions = Subscription.objects.filter(subscriber=self.request.user)
            result = []
            for subscription in subscriptions:
                serializer = serializers.SubscribeSerializer(
                    subscription.author,
                    context={'request': request}
                )
                result.append(serializer.data)
            return Response(result, status=status.HTTP_200_OK)


class IngredientViewSet(ListRetriveCreateDestroyViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter


class TagViewSet(ListRetriveCreateDestroyViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnlyPermission,)
    http_method_names = ['get', 'post', 'put', 'delete']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = RecipeFilter
    ordering = ('-pub_date',) 

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT'):
            return serializers.RecipeCreateSerializer
        return serializers.RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        url_path='favorite',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError('Этот рецепт уже в избранном.')
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                serializers.RecipeShortSerializer(recipe, context={'request': request}).data,
                status=status.HTTP_201_CREATED,
            )

        if self.request.method == 'DELETE':
            if not Favorite.objects.filter(
                user=user,
                recipe=recipe,
            ).exists():
                raise exceptions.ValidationError('Этот рецепт не в избранном.')
            favorite = get_object_or_404(
                Favorite,
                user=user,
                recipe=recipe,
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if Shopping_cart.objects.filter(
                user_to_buy=user,
                recipe_to_buy=recipe
            ).exists():
                raise exceptions.ValidationError('Этот рецепт уже в списке покупок.')
            Shopping_cart.objects.create(
                user_to_buy=user,
                recipe_to_buy=recipe,
            )
            return Response(
                serializers.RecipeShortSerializer(recipe, context={'request': request}).data,
                status=status.HTTP_201_CREATED,
            )

        if self.request.method == 'DELETE':
            if not Shopping_cart.objects.filter(
                user_to_buy=user,
                recipe_to_buy=recipe,
            ).exists():
                raise exceptions.ValidationError('Этот рецепт не в списке покупок.')
            shopping_cart = get_object_or_404(
                Shopping_cart,
                user_to_buy=user,
                recipe_to_buy=recipe,
            )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=['GET'],
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        if request.method == 'GET':
            shopping_cart = Shopping_cart.objects.filter(user_to_buy=self.request.user)
            recipes = [item.recipe_to_buy.id for item in shopping_cart]
            buy_list = RecipeIngredient.objects.filter(
                recipe__in=recipes
            ).values('ingredient').annotate(total_amount=Sum('amount'))

            file_content = 'Foodgram. Список покупок.\n\n'
            for item in buy_list:
                ingredient = Ingredient.objects.get(pk=item['ingredient'])
                amount = item['total_amount']
                file_content += (
                    f'{ingredient.name}, {amount} '
                    f'{ingredient.measurement_unit}\n'
                )
            file_name = 'shopping_cart.txt'
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
            return response

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
