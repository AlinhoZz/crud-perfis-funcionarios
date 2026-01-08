import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from employees.models import Department, EmployeeProfile


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def dept_a(db):
    return Department.objects.create(name="TI")


@pytest.fixture()
def dept_b(db):
    return Department.objects.create(name="Comercial")


def _mk_user(username: str, password: str = "12345678"):
    u = User.objects.create(username=username, email=f"{username}@email.com")
    u.set_password(password)
    u.save()
    return u


@pytest.fixture()
def superuser(db):
    return User.objects.create_superuser(
        username="super", email="super@email.com", password="12345678"
    )


@pytest.fixture()
def manager_a(db, dept_a):
    u = _mk_user("manager_a")
    EmployeeProfile.objects.create(
        user=u, department=dept_a, role=EmployeeProfile.Role.MANAGER
    )
    return u


@pytest.fixture()
def manager_b(db, dept_b):
    u = _mk_user("manager_b")
    EmployeeProfile.objects.create(
        user=u, department=dept_b, role=EmployeeProfile.Role.MANAGER
    )
    return u


@pytest.fixture()
def staff_a(db, dept_a):
    u = _mk_user("staff_a")
    EmployeeProfile.objects.create(
        user=u, department=dept_a, role=EmployeeProfile.Role.STAFF
    )
    return u


@pytest.fixture()
def staff_b(db, dept_b):
    u = _mk_user("staff_b")
    EmployeeProfile.objects.create(
        user=u, department=dept_b, role=EmployeeProfile.Role.STAFF
    )
    return u


@pytest.fixture()
def profile_staff_a(db, staff_a):
    return staff_a.employee_profile


@pytest.fixture()
def profile_staff_b(db, staff_b):
    return staff_b.employee_profile


# ------------------------
# AUTH / JWT
# ------------------------
@pytest.mark.django_db
def test_login_returns_jwt(api_client, staff_a):
    resp = api_client.post(
        "/api/auth/token/",
        {"username": "staff_a", "password": "12345678"},
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data


# ------------------------
# LIST / RETRIEVE
# ------------------------
@pytest.mark.django_db
def test_list_requires_auth(api_client):
    resp = api_client.get("/api/employees/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_staff_cannot_list(api_client, staff_a):
    api_client.force_authenticate(user=staff_a)
    resp = api_client.get("/api/employees/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_super_lists_all(api_client, superuser, profile_staff_a, profile_staff_b):
    api_client.force_authenticate(user=superuser)
    resp = api_client.get("/api/employees/")
    assert resp.status_code == 200
    assert len(resp.data) >= 2


@pytest.mark.django_db
def test_manager_lists_only_own_department(
    api_client, manager_a, profile_staff_a, profile_staff_b
):
    api_client.force_authenticate(user=manager_a)
    resp = api_client.get("/api/employees/")
    assert resp.status_code == 200

    ids = {item["id"] for item in resp.data}
    assert profile_staff_a.id in ids
    assert profile_staff_b.id not in ids


@pytest.mark.django_db
def test_manager_cannot_retrieve_other_department_returns_403(
    api_client, manager_a, profile_staff_b
):
    api_client.force_authenticate(user=manager_a)
    resp = api_client.get(f"/api/employees/{profile_staff_b.id}/")
    assert resp.status_code == 403


# ------------------------
# UPDATE
# ------------------------
@pytest.mark.django_db
def test_manager_can_update_user_fields_same_department(api_client, manager_a, profile_staff_a):
    api_client.force_authenticate(user=manager_a)
    resp = api_client.patch(
        f"/api/employees/{profile_staff_a.id}/",
        {"user": {"email": "novo@email.com"}},
        format="json",
    )
    assert resp.status_code == 200
    profile_staff_a.user.refresh_from_db()
    assert profile_staff_a.user.email == "novo@email.com"


@pytest.mark.django_db
def test_manager_cannot_change_department_or_role(api_client, manager_a, profile_staff_a, dept_a):
    api_client.force_authenticate(user=manager_a)

    resp = api_client.patch(
        f"/api/employees/{profile_staff_a.id}/",
        {"department": dept_a.id},
        format="json",
    )
    assert resp.status_code == 403

    resp = api_client.patch(
        f"/api/employees/{profile_staff_a.id}/",
        {"role": EmployeeProfile.Role.MANAGER},
        format="json",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_manager_cannot_update_other_department(api_client, manager_a, profile_staff_b):
    api_client.force_authenticate(user=manager_a)
    resp = api_client.patch(
        f"/api/employees/{profile_staff_b.id}/",
        {"user": {"email": "x@email.com"}},
        format="json",
    )
    assert resp.status_code == 403


# ------------------------
# DELETE
# ------------------------
@pytest.mark.django_db
def test_manager_cannot_delete_self(api_client, manager_a):
    api_client.force_authenticate(user=manager_a)
    profile = manager_a.employee_profile
    resp = api_client.delete(f"/api/employees/{profile.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_manager_can_delete_same_department_staff(api_client, manager_a, profile_staff_a):
    api_client.force_authenticate(user=manager_a)
    resp = api_client.delete(f"/api/employees/{profile_staff_a.id}/")
    assert resp.status_code == 204
    assert not User.objects.filter(username="staff_a").exists()
    assert not EmployeeProfile.objects.filter(id=profile_staff_a.id).exists()


@pytest.mark.django_db
def test_manager_cannot_delete_other_department(api_client, manager_a, profile_staff_b):
    api_client.force_authenticate(user=manager_a)
    resp = api_client.delete(f"/api/employees/{profile_staff_b.id}/")
    assert resp.status_code == 403
