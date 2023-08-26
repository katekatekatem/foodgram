import base64

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes import models
from users.models import CustomUser
from users.validators import names_validator_reserved, symbols_validator


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed',
        )


class UserRegistrationSerializer(UserCreateSerializer):
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
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
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
    id = serializers.IntegerField(min_value=1)
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = models.RecipeIngredient
        fields = ('amount', 'id')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'color', 'slug')


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        ingredients = models.RecipeIngredient.objects.filter(recipe=obj)
        serializer = RecipeIngredientSerializer(ingredients, many=True)
        return serializer.data


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True,
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = ('name', 'text', 'ingredients', 'tags', 'image', 'cooking_time', 'author')

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
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
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
