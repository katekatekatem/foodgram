from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shopping_cart, Tag)
from users.models import CustomUser, Subscription

from . import serializers
from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetriveCreateDestroyViewSet, ListRetriveCreateViewSet
from .pagination import CustomPageNumberPagination
from .permissions import IsAdminOrAuthorOrReadOnlyPermission


class UserViewSet(ListRetriveCreateViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserRegistrationSerializer
        if self.action == 'subscriptions':
            return serializers.SubscribeSerializer
        return serializers.CustomUserSerializer

    def get_permissions(self):
        if self.action == 'create' or self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

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
                serializers.SubscribeSerializer(
                    author,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED,
            )

        if self.request.method == 'DELETE':
            if not Subscription.objects.filter(
                subscriber=subscriber,
                author=author,
            ).exists():
                raise exceptions.ValidationError(
                    'Такой подписки не существует.'
                )
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
            user = self.request.user
            user_subscriptions = user.subscriber.all()
            authors = [item.author.id for item in user_subscriptions]
            queryset = CustomUser.objects.filter(pk__in=authors)
            paginated_queryset = self.paginate_queryset(queryset)
            serializer = self.get_serializer(paginated_queryset, many=True)
            return self.get_paginated_response(serializer.data)


class IngredientViewSet(ListRetriveCreateDestroyViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ListRetriveCreateDestroyViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnlyPermission,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering = ('-pub_date',)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
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
                raise exceptions.ValidationError(
                    'Этот рецепт уже в избранном.'
                )
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                serializers.RecipeShortSerializer(
                    recipe,
                    context={'request': request}
                ).data,
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
                raise exceptions.ValidationError(
                    'Этот рецепт уже в списке покупок.'
                )
            Shopping_cart.objects.create(
                user_to_buy=user,
                recipe_to_buy=recipe,
            )
            return Response(
                serializers.RecipeShortSerializer(
                    recipe,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED,
            )

        if self.request.method == 'DELETE':
            if not Shopping_cart.objects.filter(
                user_to_buy=user,
                recipe_to_buy=recipe,
            ).exists():
                raise exceptions.ValidationError(
                    'Этот рецепт не в списке покупок.'
                )
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
            shopping_cart = Shopping_cart.objects.filter(
                user_to_buy=self.request.user
            )
            recipes = [item.recipe_to_buy.id for item in shopping_cart]
            buy_list = RecipeIngredient.objects.filter(
                recipe__in=recipes
            ).values('ingredient').annotate(amount=Sum('amount'))

            final_buy_list = {}
            for item in buy_list:
                ingredient = Ingredient.objects.get(pk=item['ingredient'])
                if ingredient in final_buy_list:
                    final_buy_list[ingredient] += item['amount']
                else:
                    final_buy_list[ingredient] = item['amount']

            file_content = 'Foodgram. Список покупок.\n\n'
            for item in final_buy_list:
                file_content += (
                    f'{item.name}, {final_buy_list[item]} '
                    f'{item.measurement_unit}\n'
                )
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=to_buy.txt'
            return response

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
