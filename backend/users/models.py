from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from backend import constants


class User(AbstractUser):
    """Модель для пользователей"""
    first_name = models.CharField(
        _('first name'),
        max_length=constants.USER_NAME_LENGTH,
        blank=False
    )
    last_name = models.CharField(
        _('last name'),
        max_length=constants.USER_NAME_LENGTH,
        blank=False
    )
    email = models.EmailField(
        _('email address'),
        unique=True
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        null=True,
        default=''
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель для подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriber'
    )
    subscribed_on = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписан на:',
        related_name='subscribed'
    )

    class Meta:
        verbose_name = 'подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribed_on'],
                name='unique_user_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('subscribed_on')),
                name='no_self_subscribe',
            ),
        ]
