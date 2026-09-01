from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage, Routine


class DiagnosticFlowTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Take the diagnostic")

    def _answer_quiz(self, experience="some_routine"):
        concern = self.client.get(reverse("diagnostic_step", args=[1])).context["form"].fields["concern"].queryset.first()
        self.client.post(reverse("diagnostic_step", args=[1]), {"concern": concern.pk})
        skin_type = self.client.get(reverse("diagnostic_step", args=[2])).context["form"].fields["skin_type"].queryset.first()
        self.client.post(reverse("diagnostic_step", args=[2]), {"skin_type": skin_type.pk})
        self.client.post(reverse("diagnostic_step", args=[3]), {"experience": experience})
        return self.client.post(reverse("diagnostic_step", args=[4]), {}, follow=True)

    def test_quiz_produces_a_routine_with_am_and_pm_steps(self):
        response = self._answer_quiz()
        self.assertRedirects(response, reverse("routine_result"))
        self.assertEqual(len(response.context["am_steps"]), 4)
        self.assertEqual(len(response.context["pm_steps"]), 3)

    def test_beginner_routine_has_fewer_steps(self):
        response = self._answer_quiz(experience="beginner")
        self.assertEqual(len(response.context["am_steps"]), 3)
        self.assertEqual(len(response.context["pm_steps"]), 2)

    def test_saving_a_routine_requires_login_then_persists_it(self):
        self._answer_quiz()
        response = self.client.get(reverse("save_routine"))
        self.assertRedirects(response, f"{reverse('signup')}?next={reverse('save_routine')}")

        User.objects.create_user(username="andreea", password="SuperSecret123!")
        self.client.login(username="andreea", password="SuperSecret123!")
        response = self.client.get(reverse("save_routine"), follow=True)
        self.assertRedirects(response, reverse("my_routines"))
        self.assertEqual(Routine.objects.filter(user__username="andreea").count(), 1)

    def test_signup_next_rejects_external_redirect(self):
        response = self.client.post(
            f"{reverse('signup')}?next=https://evil.example/phish",
            {
                "username": "someone",
                "password1": "SuperSecret123!",
                "password2": "SuperSecret123!",
            },
        )
        self.assertRedirects(response, reverse("home"))

    def test_routine_detail_404s_for_another_users_routine(self):
        self._answer_quiz()
        owner = User.objects.create_user(username="owner", password="SuperSecret123!")
        self.client.login(username="owner", password="SuperSecret123!")
        self.client.get(reverse("save_routine"))
        routine = Routine.objects.get(user=owner)

        other = User.objects.create_user(username="someone_else", password="SuperSecret123!")
        self.client.login(username="someone_else", password="SuperSecret123!")
        response = self.client.get(reverse("routine_detail", args=[routine.pk]))
        self.assertEqual(response.status_code, 404)


class AboutContactPageTests(TestCase):
    def test_about_page_loads(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

    def test_contact_form_saves_message(self):
        response = self.client.post(
            reverse("contact"),
            {
                "subject": "product",
                "name": "Andreea",
                "email": "andreea@example.com",
                "message": "Hello!",
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        saved = ContactMessage.objects.first()
        self.assertEqual(saved.email, "andreea@example.com")
        self.assertEqual(saved.subject, "product")
