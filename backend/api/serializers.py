from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from foodgram_backend.constants import USERNAME_LENGHT
from recipes import models
from users.models import CustomUser, Subscription
from users.validators import names_validator_reserved, symbols_validator


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return bool(
            self.context['request']
            and not user.is_anonymous
            and obj.author.filter(subscriber=user).exists()
        )

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed',
        )


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""

    username = serializers.CharField(
        max_length=USERNAME_LENGHT,
        required=True,
        validators=[symbols_validator, names_validator_reserved],
    )
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        max_length=USERNAME_LENGHT,
        required=True,
    )

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'id')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов (короткий)."""

    image = serializers.ReadOnlyField(source='image.url')

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, data):
        subscriber = self.instance
        author = self.context.get('request').user
        if Subscription.objects.filter(
            subscriber=subscriber,
            author=author
        ).exists():
            raise serializers.ValidationError(
                detail='Подписка уже существует.'
            )
        if subscriber == author:
            raise serializers.ValidationError(
                detail='Невозможно подписаться на самого себя.'
            )
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""

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
    """Сериализатор для чтения связующей модели рецептов и ингредиентов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField()

    class Meta:
        model = models.RecipeIngredient
        fields = ('amount', 'id', 'name', 'measurement_unit')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания записей в связующей модели
    рецептов и ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all(),
        source='ingredient__id',
    )
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1, max_value=10000)

    class Meta:
        model = models.RecipeIngredient
        fields = ('amount', 'id')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = serializers.ReadOnlyField(source='image.url')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = models.Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return bool(
            self.context['request']
            and not user.is_anonymous
            and obj.recipe.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return bool(
            self.context['request']
            and not user.is_anonymous
            and obj.recipe_to_buy.filter(user_to_buy=user).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования рецептов."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True,
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1, max_value=3000)

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

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                'Список тегов не может быть пустым.'
            )
        return data

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым.'
            )
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return data

    def recipeingredient_create(self, recipe, ingredients):
        data = (
            models.RecipeIngredient(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=models.Ingredient.objects.get(id=ingredient['id']),
            ) for ingredient in ingredients
        )
        models.RecipeIngredient.objects.bulk_create(data)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = models.Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.recipeingredient_create(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        models.RecipeTag.objects.filter(recipe=instance).delete()
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        models.RecipeIngredient.objects.filter(recipe=instance).delete()
        self.recipeingredient_create(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = models.Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=models.Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = models.Shopping_cart
        fields = ('user_to_buy', 'recipe_to_buy')
        validators = [
            UniqueTogetherValidator(
                queryset=models.Shopping_cart.objects.all(),
                fields=('user_to_buy', 'recipe_to_buy')
            )
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписок."""

    class Meta:
        model = Subscription
        fields = ('subscriber', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('subscriber', 'author')
            )
        ]
