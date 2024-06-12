from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from common.models import CommonDateModel

class UserManager(BaseUserManager):
    def create_user(self, **extra_fields):
        user = self.model(**extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(**extra_fields)


class User(AbstractBaseUser, CommonDateModel):
    """시스템 내 개별 사용자를 나타내는 사용자 모델입니다."""

    GENDER_CHOICES = [
        (False, 'Male'),
        (True, 'Female'),
    ]
    gender = models.BooleanField(choices=GENDER_CHOICES, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, default=None)
    nickname = models.CharField(max_length=20, unique=True, null=True, blank=True)
    image = models.CharField(null=True, blank=True)
    is_staff = models.BooleanField(default=False, null=True, blank=True)
    is_login = models.BooleanField(default=False, null=True, blank=True)
    is_alert = models.BooleanField(default=True, null=True, blank=True)
    social_id = models.CharField(max_length=100, null=True, unique=True)
    social_type = models.CharField(max_length=15, null=True)
    objects = UserManager()

    USERNAME_FIELD = "social_id"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.social_id


class User_refresh_token(CommonDateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=1024, null=True, blank=True)
    estimate = models.DateTimeField(auto_now_add=True, null=True, blank=True)