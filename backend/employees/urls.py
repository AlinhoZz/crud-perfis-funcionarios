from rest_framework.routers import DefaultRouter

from .views import EmployeeProfileViewSet

router = DefaultRouter()
router.register(r"employees", EmployeeProfileViewSet, basename="employees")

urlpatterns = router.urls
