from django.conf import settings
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes import models
from users.models import CustomUser, Subscription
from users.validators import names_validator_reserved, symbols_validator


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериалайзер для чтения модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            subscriber=user,
            author=obj
        ).exists()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed',
        )


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериалайзер для регистрации пользователей."""

    username = serializers.CharField(
        max_length=settings.USERNAME_LENGHT,
        required=True,
        validators=[symbols_validator, names_validator_reserved],
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_LENGHT,
        required=True,
    )
    password = serializers.CharField(
        max_length=settings.USERNAME_LENGHT,
        required=True,
    )

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериалайзер для чтения рецептов (короткий)."""

    image = serializers.ReadOnlyField(source='image.url')

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            subscriber=user,
            author=author
        ).exists()

    def get_recipes(self, instance):
        queryset = models.Recipe.objects.filter(author__id=instance.id)
        return RecipeShortSerializer(queryset, many=True).data

    def get_recipes_count(self, instance):
        queryset = models.Recipe.objects.filter(author__id=instance.id)
        return queryset.count()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели ингредиентов."""

    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')
        validators = [
            UniqueTogetherValidator(
                queryset=models.Ingredient.objects.all(),
                fields=('name', 'measurement_unit')
            )
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для чтения связующей модели рецептов и ингредиентов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = models.RecipeIngredient
        fields = ('amount', 'id', 'name', 'measurement_unit')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания записей в связующей модели
    рецептов и ингредиентов."""

    id = serializers.IntegerField(min_value=1)
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = models.RecipeIngredient
        fields = ('amount', 'id')


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели тегов."""

    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для чтения рецептов."""

    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = serializers.ReadOnlyField(source='image.url')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = models.Recipe
        exclude = ('pub_date',)

    def get_ingredients(self, obj):
        ingredients = models.RecipeIngredient.objects.filter(recipe=obj)
        serializer = RecipeIngredientSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return models.Favorite.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return models.Shopping_cart.objects.filter(
            user_to_buy=user, recipe_to_buy=recipe
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания и редактирования рецептов."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True,
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = ('name', 'text', 'ingredients', 'tags', 'image',
                  'cooking_time', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=models.Recipe.objects.all(),
                fields=('name', 'text')
            )
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = models.Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            models.RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=models.Ingredient.objects.get(id=ingredient['id']),
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        tags = validated_data.pop('tags')
        models.RecipeTag.objects.filter(recipe=instance).delete()
        instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients')
        models.RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            models.RecipeIngredient.objects.update_or_create(
                recipe=instance,
                amount=ingredient['amount'],
                ingredient=models.Ingredient.objects.get(id=ingredient['id']),
            )

        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data
