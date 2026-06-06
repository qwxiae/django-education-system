from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from apps.users.models import Role, UserRole

from .models import Category, Course, Enrollment, Module


class BaseTestClass(TestCase):
    def setUp(self):
        self.client = Client()

        self.category = Category.objects.create(name="History")
        self.role = Role.objects.create(name="instructor")
        Role.objects.create(name="student")

        self.User = get_user_model()
        # must use create_user to hash password: login uses hashed passwords
        self.author = self.User.objects.create_user(
            username="coursetest",
            email="test_courses@test.com",
            password="testingCourses",
        )
        self.student = self.User.objects.create_user(
            username="coursestudent",
            email="test_student@test.com",
            password="testingStudent",
        )

        UserRole.objects.create(user=self.author, role=self.role)

        self.course = Course.objects.create(
            author=self.author,
            category=self.category,
            title="Test Course",
            is_published=True,
        )
        self.unpublished = Course.objects.create(
            author=self.author,
            category=self.category,
            title="Unpublished",
            is_published=False,
        )


class CategoryTestCase(BaseTestClass):
    def test_create_category(self):
        cat = Category.objects.create(name="Philosophy")
        self.assertEqual(cat.name, "Philosophy")
        self.assertEqual(cat.slug, "philosophy")

    def test_create_duplicate_category(self):
        cat = Category.objects.create(name="Philosophy")
        self.assertEqual(cat.name, "Philosophy")

        # fails because of similar slug
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="philosophy")

    def test_get_category(self):
        response = self.client.get(reverse("courses:catalog"), {"category": "history"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_category"], "history")


class CourseTestCase(BaseTestClass):
    def test_delete_author_and_category_course_stays(self):
        self.author.delete()
        self.category.delete()
        does_course_exist = Course.objects.filter(slug="test-course")
        self.assertTrue(does_course_exist)

    def test_create_course_with_duplicate_name(self):
        """
        Duplicate name are allowed.
        Slugs are different automatically
        """

        course2 = Course.objects.create(
            author=self.author,
            category=self.category,
            title="Test Course",
            is_published=True,
        )
        self.assertIsNotNone(course2)

    def test_get_courses(self):
        response = self.client.get(reverse("courses:catalog"))
        self.assertEqual(response.status_code, 200)

    def test_get_course(self):
        response = self.client.get(
            reverse("courses:course_detail", kwargs={"slug": self.course.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["course"], self.course)

    def test_slug_not_updated_on_title_change(self):
        """Changing title does not regenerate slug."""
        prev_slug = self.course.slug
        Course.objects.filter(slug=prev_slug).update(title="New title")

        current_slug = self.course.slug
        self.assertEqual(prev_slug, current_slug)


class ModuleTestCase(BaseTestClass):
    def setUp(self):
        super().setUp()
        Module.objects.create(course=self.course, title="M1", order=1)
        Module.objects.create(course=self.course, title="M2", order=2)

    def test_get_course_modules(self):
        response = self.client.get(
            reverse("courses:course_detail", kwargs={"slug": self.course.slug})
        )
        self.assertEqual(
            list(response.context["modules"]),
            list(Module.objects.filter(course=self.course)),
        )

    def test_unique_order_per_course(self):
        with self.assertRaises(IntegrityError):
            Module.objects.create(course=self.course, title="M2", order=2)

    def test_same_order_different_courses(self):
        course2 = Course.objects.create(
            author=self.author,
            category=self.category,
            title="Test Course",
            is_published=True,
        )
        module = Module.objects.create(course=course2, title="M2", order=2)
        self.assertIsNotNone(module)


class EnrollmentTestCase(BaseTestClass):
    def setUp(self):
        super().setUp()
        logged_in = self.client.login(
            email="test_student@test.com", password="testingStudent"
        )
        self.assertTrue(logged_in)

    def test_enroll_unauth_user(self):
        self.client.logout()
        response = self.client.post(
            reverse("courses:enroll", kwargs={"slug": self.course.slug}),
            # header
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 302)

    def test_enroll_auth_user(self):
        response = self.client.post(
            reverse("courses:enroll", kwargs={"slug": self.course.slug}),
            # header
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Enrollment.objects.filter(user=self.student, course=self.course).exists()
        )

    def test_unenroll(self):
        self.enrollment = Enrollment.objects.create(
            user=self.student, course=self.course
        )
        response = self.client.post(
            reverse("courses:unenroll", kwargs={"slug": self.course.slug}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Enrollment.objects.filter(user=self.student, course=self.course).exists()
        )

    def test_duplicate_enroll(self):
        """Enrolling twice should not create two enrollments"""
        Enrollment.objects.create(user=self.student, course=self.course)
        self.client.post(
            reverse("courses:enroll", kwargs={"slug": self.course.slug}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(
            Enrollment.objects.filter(user=self.student, course=self.course).count(), 1
        )

    def test_enroll_unpublished_course(self):
        response = self.client.post(
            reverse("courses:enroll", kwargs={"slug": self.unpublished.slug}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
