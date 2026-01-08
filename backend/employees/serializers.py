from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import Department, EmployeeProfile


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password")
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True},
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
            "email": {"required": False, "allow_blank": True},
        }


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer(required=False)

    class Meta:
        model = EmployeeProfile
        fields = ("id", "user", "department", "role", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")

        if self.instance is not None:
            user_data = attrs.get("user") or {}

            for f in ("username", "first_name", "last_name", "email"):
                if f in user_data and not (user_data.get(f) or "").strip():
                    raise serializers.ValidationError({"user": {f: "Este campo não pode ser vazio."}})

            if request and request.user and request.user.is_authenticated and not request.user.is_superuser:
                if "department" in attrs:
                    raise PermissionDenied("Gestor não pode alterar o departamento.") from None
                if "role" in attrs:
                    raise PermissionDenied("Gestor não pode alterar o papel (role).") from None

            return attrs

        user_data = attrs.get("user") or {}

        required_fields = ["username", "first_name", "last_name", "email", "password"]
        missing = [f for f in required_fields if not (user_data.get(f) or "").strip()]
        if missing:
            raise serializers.ValidationError({"user": f"Campos obrigatórios ausentes: {', '.join(missing)}"})

        dept = attrs.get("department")
        if not isinstance(dept, Department):
            raise serializers.ValidationError({"department": "Departamento inválido."})

        if request and request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return attrs

            try:
                requester = EmployeeProfile.objects.select_related("department").get(user=request.user)
            except EmployeeProfile.DoesNotExist:
                raise serializers.ValidationError("Usuário solicitante não possui perfil.") from None

            if requester.role != EmployeeProfile.Role.MANAGER:
                raise serializers.ValidationError("Apenas super ou gestor pode criar perfis.")

            if requester.department.pk != dept.pk:
                raise serializers.ValidationError("Gestor só pode criar perfis do próprio departamento.")

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        raw_password = (user_data.pop("password") or "").strip()

        user = User(**user_data)
        user.set_password(raw_password)
        user.save()

        profile = EmployeeProfile.objects.create(user=user, **validated_data)
        return profile

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        if user_data:
            raw_password = (user_data.pop("password", None) or "").strip()

            for field in ("username", "first_name", "last_name", "email"):
                if field in user_data:
                    setattr(instance.user, field, user_data[field])

            if raw_password:
                instance.user.set_password(raw_password)

            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
