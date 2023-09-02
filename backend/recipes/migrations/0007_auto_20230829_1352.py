# Generated by Django 3.2 on 2023-08-29 10:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_recipe_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('user__username',), 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'ordering': ('recipe',), 'verbose_name': 'Рецепты и ингредиенты', 'verbose_name_plural': 'Рецепты и ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipetag',
            options={'ordering': ['recipe'], 'verbose_name': 'Рецепты и теги', 'verbose_name_plural': 'Рецепты и теги'},
        ),
        migrations.AlterModelOptions(
            name='shopping_cart',
            options={'ordering': ('user_to_buy__username',), 'verbose_name': 'Список покупок', 'verbose_name_plural': 'Список покупок'},
        ),
    ]