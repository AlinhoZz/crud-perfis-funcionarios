from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import EmployeeProfile, Department
from .permissions import IsSuperOrManager
from .serializers import EmployeeProfileSerializer, DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    
    def get_permissions(self):
        """
        Define permissões dinâmicas:
        - Métodos de leitura (GET, HEAD, OPTIONS): Qualquer usuário autenticado.
        - Métodos de escrita (POST, PUT, DELETE): Apenas Admin (superuser).
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsSuperOrManager]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["department"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]

    def perform_destroy(self, instance):
        if self.request.user == instance.user:
            raise PermissionDenied("Você não pode deletar seu próprio usuário.") from None

        instance.user.delete()

    def get_queryset(self):
        qs = EmployeeProfile.objects.select_related("user", "department").all()

        if self.request.user.is_superuser:
            return qs

        try:
            requester = EmployeeProfile.objects.select_related("department").get(
                user=self.request.user
            )
        except EmployeeProfile.DoesNotExist:
            return qs.none()

        return qs.filter(department=requester.department)

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            if self.request.user.is_authenticated and not self.request.user.is_superuser:
                pk = self.kwargs.get(self.lookup_field)
                if pk and EmployeeProfile.objects.filter(pk=pk).exists():
                    raise PermissionDenied(
                        "Acesso negado: perfil fora do seu departamento."
                    ) from None
            raise