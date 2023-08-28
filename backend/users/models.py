from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.constraints import CheckConstraint, UniqueConstraint

from .validators import names_validator_reserved, symbols_validator


USER = 'user'
ADMIN = 'admin'

ROLES = (
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
)


class CustomUser(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=settings.USERNAME_LENGHT,
        unique=True,
        validators=[
            symbols_validator,
            names_validator_reserved,
        ],
    )
    email = models.EmailField(
        max_length=settings.EMAIL_LENGHT,
        unique=True,
    )
    first_name = models.CharField(
        max_length=settings.USERNAME_LENGHT
    )
    last_name = models.CharField(
        max_length=settings.USERNAME_LENGHT
    )
    password = models.CharField(
        max_length=settings.USERNAME_LENGHT
    )
    role = models.CharField(
        choices=ROLES,
        max_length=max(len(role) for role, _ in ROLES),
        default=USER
    )
    is_subscribed = models.BooleanField(default=False)

    class Meta(AbstractUser.Meta):
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.role == ADMIN or self.is_superuser


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
