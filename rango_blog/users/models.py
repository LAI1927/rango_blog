from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    mobile = models.CharField(max_length=11, unique=True, blank=False)  # Phone number field
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)  # Avatar
    user_desc = models.CharField(max_length=500, blank=True)  # Personal profile

    USERNAME_FIELD = 'mobile'  # Modify the authentication field to mobile phone number
    REQUIRED_FIELDS = ['username', 'email']  # Create super administrator

    # Used to define metadata for the model
    class Meta:
        db_table = 'tb_user'
        verbose_name = 'User Information'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.mobile

