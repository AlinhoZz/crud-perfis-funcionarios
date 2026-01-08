from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ["name"]

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Funcionário"
        verbose_name_plural = "Perfis de Funcionários"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user.username} ({self.department.name})"
