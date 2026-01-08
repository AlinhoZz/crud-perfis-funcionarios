from rest_framework.permissions import BasePermission

from .models import EmployeeProfile


class IsSuperOrManager(BasePermission):
    """
    Super: acesso total
    Gestor: acesso ao CRUD, mas limitado ao próprio departamento (object-level)
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            profile = EmployeeProfile.objects.select_related("department").get(user=request.user)
        except EmployeeProfile.DoesNotExist:
            return False

        return profile.role == EmployeeProfile.Role.MANAGER

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        try:
            requester = EmployeeProfile.objects.select_related("department").get(user=request.user)
        except EmployeeProfile.DoesNotExist:
            return False

        return requester.department.pk == obj.department.pk
