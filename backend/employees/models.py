from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self) -> str:
        return self.name


class EmployeeProfile(models.Model):
    class Role(models.TextChoices):
        MANAGER = "MANAGER", "Gestor"
        STAFF = "STAFF", "Colaborador"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF,
    )

    def __str__(self) -> str:
        return f"{self.user.username} ({self.department.name})"
