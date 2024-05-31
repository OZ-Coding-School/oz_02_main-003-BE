from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from common.models import CommonDateModel


class UserManager(BaseUserManager):
    def create_user(self, email, name=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, CommonDateModel):
    """시스템 내 개별 사용자를 나타내는 사용자 모델입니다."""

    GENDER_CHOICES = [
        (False, 'Male'),
        (True, 'Female'),
    ]
    email = models.EmailField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.BooleanField(choices=GENDER_CHOICES, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, default=None)
    nickname = models.CharField(max_length=20, unique=True, null=True, blank=True)
    image = models.URLField(null=True, default=None, blank=True)
    is_staff = models.BooleanField(default=False, null=True, blank=True)
    is_login = models.BooleanField(default=False, null=True, blank=True)
    is_alert = models.BooleanField(default=False, null=True, blank=True)
    social = models.CharField(max_length=15, null=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email


class User_refresh_token(CommonDateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, null=True, blank=True)
    estimate = models.DateTimeField(auto_now_add=True, null=True, blank=True)
