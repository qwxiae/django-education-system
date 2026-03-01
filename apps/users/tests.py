from django.test import TestCase, Client
from .models import User, Profile, Role, UserRole
from django.urls import reverse

'''
    >>> c = Client()
    >>> response = c.post("/login/", {"username": "john", "password": "smith"})
    >>> response.status_code
    200
    >>> response = c.get("/customer/details/")
    >>> response.content
    b'<!DOCTYPE html...'
'''

class UserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        Role.objects.create(name="student")
        self.user = User.objects.create_user(
            email="test@test.com",
            password="Xk9#mP2$qL5nR8@w123",
        )
    
    def test_create_user(self):
        user = User.objects.get(email="test@test.com")
        self.assertEqual(user.email, "test@test.com")
        self.assertTrue(user.is_active)

    def test_create_users_profile(self):
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertIsInstance(self.user.profile, Profile)

    def test_register_user(self):
        response = self.client.post(reverse("users:register"), {
            "email": "test2@test.com",
            "password1": "Xk9#mP2$qL5nR8@w123",
            "password2": "Xk9#mP2$qL5nR8@w123",
            }
        )
        # redirect after register
        self.assertEqual(response.status_code, 302)

    def test_login_user(self):
        response = self.client.post(reverse("users:login"), {
            "email": "test@test.com",
            "password": "Xk9#mP2$qL5nR8@w123",
            }
        )
        # redirect after login
        self.assertEqual(response.status_code, 302)

    def test_logout_user(self):
        self.client.login(email="test@test.com", password="Xk9#mP2$qL5nR8@w123")
        response = self.client.get(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)

    def test_login_page(self):
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_incorrect_data(self):
        response = self.client.post(reverse("users:login"), {
            "email": "test@test.com",
            "password": "wrongpassword",
        })
        # stay on login page
        self.assertEqual(response.status_code, 200)
    
    def test_register_page(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_page_incorrect_data(self):
        response = self.client.post(reverse("users:register"), {
            "email": "bademail",
            "password1": "12sjdJHGk!2",
            "password2": "12sjdJHGk!3"
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="bademail").exists())

    def test_logout_page(self):
        self.client.login(email="test@test.com", password="Xk9#mP2$qL5nR8@w123")
        response = self.client.get(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)

    
class ProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        Role.objects.create(name="student")
        self.user = User.objects.create_user(
            email="test@test.com",
            password="Xk9#mP2$qL5nR8@w123"
        )
        self.client.login(email="test@test.com", password="Xk9#mP2$qL5nR8@w123")

    def test_get_profile_page(self):
        other_user = User.objects.create_user(
            email="other_test@test.com",
            password="Xk9#mP2$qL5nR8@w321",
        )
        response = self.client.get(
            reverse("users:public_profile", kwargs={"user_id": other_user.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_my_profile_page(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)

    def test_update_my_profile_page(self):
        response = self.client.post(reverse("users:profile_edit"), {
            "first_name": "John",
            "last_name": "Doe",
            "bio": "Lorem ipsum...",
            "phone": "123456789",
        })
        self.assertEqual(response.status_code, 302)
        # TODO: why this
        self.user.profile.refresh_from_db()
        self.assertAlmostEqual(self.user.profile.first_name, "John")


class RoleTestCase(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="student")

    def test_create_role(self):
        self.assertEqual(self.role.name, "student")
        self.assertTrue(Role.objects.filter(name="student").exists())

    def test_delete_role(self):
        self.role.delete()
        self.assertFalse(Role.objects.filter(name="student").exists())

class UserRoleTestCase(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="student")
        self.user = User.objects.create_user(
            email="test@test.com",
            password="Xk9#mP2$qL5nR8@w123"
        )
        # No need to create as Signal has already created it
        self.user_role = UserRole.objects.get(user=self.user, role=self.role)

    def test_delete_role_from_userrole(self):
        from django.db.models import ProtectedError

        with self.assertRaises(ProtectedError):
            self.role.delete()

    def test_delete_user_from_userrole(self):
        user_id = self.user.id
        self.user.delete()
        # TODO: where did user_id come from?
        self.assertFalse(UserRole.objects.filter(user_id=user_id).exists())

    def test_update_userrole(self):
        instructor_role = Role.objects.create(name="instructor")
        self.user_role.role = instructor_role
        self.user_role.save()
        self.user_role.refresh_from_db()
        self.assertEqual(self.user_role.role.name, "instructor")