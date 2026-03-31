from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.test import TestCase
from django.urls import reverse
from .forms import User_Account_Creation_Form

#GET_USER_MODEL is a function that returns the currently active user model in the Django project. This is useful when you have a custom user model defined in your application, as it allows you to retrieve the correct user model without hardcoding its name. By using get_user_model(), you can ensure that your code works correctly regardless of whether you're using the default User model or a custom one.

class RegisterFormTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_register_form_valid_data(self):
        form = User_Account_Creation_Form(
            data={
                "username": "newuser1",
                "first_name": "Luca",
                "last_name": "M",
                "email": "newuser1@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )
        self.assertTrue(form.is_valid())

    def test_register_form_rejects_duplicate_email(self):
        self.User.objects.create_user(
            username="existinguser",
            email="dup@example.com",
            password="StrongPass123!",
        )

        form = User_Account_Creation_Form(
            data={
                "username": "anotheruser",
                "first_name": "Ana",
                "last_name": "B",
                "email": "dup@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_register_view_creates_user_and_redirects(self):
        response = self.client.post(
            reverse("register"),
            data={
                "username": "createdbyview",
                "first_name": "John",
                "last_name": "Doe",
                "email": "createdbyview@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302) #302 status code indicates a successful redirect after form submission, which is the expected behavior when a user is successfully registered.
        self.assertTrue(
            self.User.objects.filter(username="createdbyview").exists()
        )


class LoginTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.password = "StrongPass123!"
        self.user = self.User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password=self.password,
        )

    def test_login_page_uses_authentication_form(self):
        response = self.client.get(reverse("login"))
        #reverse function is used to generate the URL for the login view based on its name ("login"). This allows us to test the login page without hardcoding the URL, making our tests more maintainable and less prone to breakage if we change our URL patterns in the future.

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], AuthenticationForm)

    def test_login_success(self):
        response = self.client.post(
            reverse("login"),
            data={"username": "loginuser", "password": self.password},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_fails_with_wrong_password(self):
        response = self.client.post(
            reverse("login"),
            data={"username": "loginuser", "password": "WrongPass123!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(
            response,
            "Please enter a correct username and password"
        )