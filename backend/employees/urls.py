from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, EmployeeProfileViewSet

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="departments")
router.register(r"employees", EmployeeProfileViewSet, basename="employees")

urlpatterns = router.urls
