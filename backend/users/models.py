from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.constraints import CheckConstraint, UniqueConstraint

from foodgram_backend.constants import USERNAME_LENGHT
from .validators import names_validator_reserved, symbols_validator


class CustomUser(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=USERNAME_LENGHT,
        unique=True,
        validators=[
            symbols_validator,
            names_validator_reserved,
        ],
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(
        max_length=USERNAME_LENGHT
    )
    last_name = models.CharField(
        max_length=USERNAME_LENGHT
    )
    # Переопределяю пароль из-за ограничения по его длине в доке
    password = models.CharField(
        max_length=USERNAME_LENGHT,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'password']

    class Meta(AbstractUser.Meta):
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""

    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='author',
    )

    class Meta:
        ordering = ('subscriber__username',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_subscriber&author',
            ),
            CheckConstraint(
                check=~models.Q(subscriber=models.F('author')),
                name='users_cannot_subscribe_to_themselves'
            ),
        ]

    def __str__(self):
        return f'Подписчик {self.subscriber}, автор {self.author}'
