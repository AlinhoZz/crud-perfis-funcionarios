from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from .models import Department, EmployeeProfile


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password")


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer(required=False)

    class Meta:
        model = EmployeeProfile
        fields = ("id", "user", "department", "role", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        if self.instance is not None:
            return attrs

        user_data = attrs.get("user") or {}
        required = ["username", "first_name", "last_name", "email"]
        missing = [f for f in required if not (user_data.get(f) or "").strip()]
        if missing:
            raise serializers.ValidationError(
                {"user": f"Campos obrigatórios ausentes: {', '.join(missing)}"}
            )

        dept = attrs.get("department")
        if not isinstance(dept, Department):
            raise serializers.ValidationError({"department": "Departamento inválido."})

        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return attrs

            try:
                requester = EmployeeProfile.objects.select_related("department").get(
                    user=request.user
                )
            except EmployeeProfile.DoesNotExist:
                raise serializers.ValidationError(
                    "Usuário solicitante não possui perfil."
                ) from None

            if requester.role != EmployeeProfile.Role.MANAGER:
                raise serializers.ValidationError("Apenas super ou gestor pode criar perfis.")

            if requester.department.pk != dept.pk:
                raise serializers.ValidationError(
                    "Gestor só pode criar perfis do próprio departamento."
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        raw_password = (user_data.pop("password", "") or "").strip()

        user = User(**user_data)
        if raw_password:
            user.set_password(raw_password)
        else:
            user.set_unusable_password()
        user.save()

        profile = EmployeeProfile.objects.create(user=user, **validated_data)
        return profile
