from django.contrib import admin

from .models import Department, EmployeeProfile


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "department", "role")
    list_filter = ("department", "role")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
