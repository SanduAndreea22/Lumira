from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage, Order, Product, Routine


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


class _FakeStripeObject(dict):
    """Minimal stand-in supporting both stripe_obj.attr and ["key"] access."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class CartCheckoutTests(TestCase):
    def setUp(self):
        self.product = Product.objects.filter(is_active=True).first()

    def test_add_to_cart_and_view(self):
        self.client.post(reverse("add_to_cart", args=[self.product.pk]))
        response = self.client.get(reverse("cart_view"))
        self.assertContains(response, self.product.name)
        self.assertContains(response, f"{self.product.price:.2f}")

    def test_remove_from_cart(self):
        self.client.post(reverse("add_to_cart", args=[self.product.pk]))
        self.client.post(reverse("remove_from_cart", args=[self.product.pk]))
        response = self.client.get(reverse("cart_view"))
        self.assertNotContains(response, self.product.name)

    def test_checkout_without_stripe_key_shows_error_and_creates_no_order(self):
        self.client.post(reverse("add_to_cart", args=[self.product.pk]))
        response = self.client.post(reverse("checkout"), follow=True)
        self.assertRedirects(response, reverse("cart_view"))
        self.assertEqual(Order.objects.count(), 0)

    @override_settings(STRIPE_SECRET_KEY="sk_test_fake")
    @patch("routines.views.stripe.checkout.Session.create")
    def test_checkout_redirects_to_stripe_when_configured(self, mock_create):
        mock_create.return_value = _FakeStripeObject(url="https://checkout.stripe.com/fake-session")
        self.client.post(reverse("add_to_cart", args=[self.product.pk]))
        response = self.client.post(reverse("checkout"))
        self.assertRedirects(
            response, "https://checkout.stripe.com/fake-session", fetch_redirect_response=False
        )
        self.assertTrue(mock_create.called)

    @override_settings(STRIPE_WEBHOOK_SECRET="whsec_fake")
    @patch("routines.views.stripe.Webhook.construct_event")
    def test_webhook_rejects_invalid_signature(self, mock_construct_event):
        mock_construct_event.side_effect = ValueError("bad payload")
        response = self.client.post(
            reverse("stripe_webhook"), data=b"{}", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(STRIPE_SECRET_KEY="sk_test_fake")
    @patch("routines.views.stripe.checkout.Session.list_line_items")
    @patch("routines.views.stripe.checkout.Session.retrieve")
    def test_checkout_success_records_order_and_clears_cart(self, mock_retrieve, mock_list_items):
        self.client.post(reverse("add_to_cart", args=[self.product.pk]))

        mock_retrieve.return_value = _FakeStripeObject(
            payment_status="paid",
            amount_total=int(self.product.price * 100),
            metadata={},
            customer_details=_FakeStripeObject(email="buyer@example.com"),
        )
        mock_list_items.return_value = _FakeStripeObject(
            data=[
                _FakeStripeObject(
                    quantity=1,
                    price=_FakeStripeObject(
                        unit_amount=int(self.product.price * 100),
                        product=_FakeStripeObject(metadata={"lumira_product_id": str(self.product.pk)}),
                    ),
                )
            ]
        )

        response = self.client.get(f"{reverse('checkout_success')}?session_id=cs_test_fake")
        self.assertEqual(response.status_code, 200)

        order = Order.objects.get(stripe_checkout_session_id="cs_test_fake")
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(order.email, "buyer@example.com")
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product, self.product)

        cart_response = self.client.get(reverse("cart_view"))
        self.assertNotContains(cart_response, self.product.name)
