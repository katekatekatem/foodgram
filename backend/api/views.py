from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shopping_cart, Tag)
from users.models import CustomUser, Subscription
from . import serializers
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrReadOnlyPermission


class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):

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
            permission_classes = (permissions.AllowAny,)
        else:
            permission_classes = (permissions.IsAuthenticated,)
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
            data = {'subscriber': subscriber.id, 'author': author.id}
            serializer = serializers.SubscriptionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            second_serializer = serializers.SubscribeSerializer(
                author,
                context={'request': request},
            )
            return Response(
                second_serializer.data,
                status=status.HTTP_201_CREATED
            )

        if self.request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                subscriber=subscriber,
                author=author,
            )
            deleted_objects_count, _ = subscription.delete()
            if not deleted_objects_count:
                raise exceptions.ValidationError(
                    'Такой подписки не существует.'
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        url_path='subscriptions',
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = self.request.user
        user_subscriptions = user.subscriber.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = CustomUser.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return serializers.RecipeCreateSerializer
        return serializers.RecipeReadSerializer

    @staticmethod
    def fav_or_shop_cart_post(serializer, data, recipe):
        serializer = serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        second_serializer = serializers.RecipeShortSerializer(recipe)
        return Response(
            second_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def save_to_text_file(self, buy_list):
        final_buy_list = {}
        for item in buy_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            if ingredient in final_buy_list:
                final_buy_list[ingredient] += item['amount']
            else:
                final_buy_list[ingredient] = item['amount']
        sorted_final_buy_list = sorted(
            final_buy_list.items(), key=lambda x: x[0].name
        )

        file_content = 'Foodgram. Список покупок.\n\n'
        for item in sorted_final_buy_list:
            ingredient = item[0]
            amount = item[1]
            file_content += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )
        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=to_buy.txt'
        return response

    @action(
        methods=['POST', 'DELETE'],
        url_path='favorite',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            data = {'user': user.id, 'recipe': recipe.id}
            return self.fav_or_shop_cart_post(
                serializers.FavoriteSerializer,
                data,
                recipe,
            )

        if self.request.method == 'DELETE':
            favorite = get_object_or_404(
                Favorite,
                user=user,
                recipe=recipe,
            )
            deleted_objects_count, _ = favorite.delete()
            if not deleted_objects_count:
                raise exceptions.ValidationError(
                    'Этот рецепт не в избранном.'
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            data = {'user_to_buy': user.id, 'recipe_to_buy': recipe.id}
            return self.fav_or_shop_cart_post(
                serializers.ShoppingCartSerializer,
                data,
                recipe,
            )

        if self.request.method == 'DELETE':
            shopping_cart = get_object_or_404(
                Shopping_cart,
                user_to_buy=user,
                recipe_to_buy=recipe,
            )
            deleted_objects_count, _ = shopping_cart.delete()
            if not deleted_objects_count:
                raise exceptions.ValidationError(
                    'Этот рецепт не в списке покупок.'
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_cart = Shopping_cart.objects.filter(
            user_to_buy=self.request.user
        )
        recipes = [item.recipe_to_buy.id for item in shopping_cart]
        buy_list = RecipeIngredient.objects.filter(
            recipe__in=recipes
        ).values('ingredient').annotate(amount=Sum('amount'))
        return self.save_to_text_file(buy_list)
