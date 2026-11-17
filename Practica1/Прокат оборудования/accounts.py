from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        CLIENT = "client", "Клиент"
        MANAGER = "manager", "Менеджер"
        ADMIN = "admin", "Администратор"

    role = models.CharField(
        max_length=10, choices=Roles.choices, default=Roles.CLIENT
    )
    phone = models.CharField("Телефон", max_length=20, blank=True)

    @property
    def is_manager(self):
        return self.role in {self.Roles.MANAGER, self.Roles.ADMIN}
