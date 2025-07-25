from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from backend import constants


class User(AbstractUser):
    first_name = models.CharField(
        _('first name'),
        max_length=constants.USER_NAME_LENGTH
    )
    last_name = models.CharField(
        _('last name'),
        max_length=constants.USER_NAME_LENGTH
    )
    email = models.EmailField(
        _('email address'),
        unique=True
    )
    subscription = models.ManyToManyField(
        'self',
        symmetrical=False
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        default=None
    )

    def __str__(self):
        return self.username
