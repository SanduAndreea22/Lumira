from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Routine


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
