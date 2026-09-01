from unittest.mock import patch

import stripe
from django.contrib.auth.models import User
from django.db import IntegrityError
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

    def test_missing_catalog_product_shows_friendly_error_instead_of_500(self):
        # If an admin deactivates every SPF product, the routine builder has
        # nothing to put in that step — should degrade gracefully, not 500.
        Product.objects.filter(category="spf").update(is_active=False)
        response = self._answer_quiz()
        self.assertRedirects(response, reverse("home"))

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

    def test_logout_link_is_a_post_form_not_a_get_link(self):
        User.objects.create_user(username="andreea", password="SuperSecret123!")
        self.client.login(username="andreea", password="SuperSecret123!")
        response = self.client.get(reverse("home"))
        self.assertContains(response, f'method="post" action="{reverse("logout")}"')

    def test_logout_works_via_post(self):
        User.objects.create_user(username="andreea", password="SuperSecret123!")
        self.client.login(username="andreea", password="SuperSecret123!")
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("my_routines"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('my_routines')}")


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

    @override_settings(STRIPE_SECRET_KEY="sk_test_fake")
    @patch("routines.views.stripe.checkout.Session.create")
    def test_checkout_failure_shows_friendly_error_instead_of_500(self, mock_create):
        mock_create.side_effect = stripe.error.StripeError("boom")
        self.client.post(reverse("add_to_cart", args=[self.product.pk]))
        response = self.client.post(reverse("checkout"), follow=True)
        self.assertRedirects(response, reverse("cart_view"))
        self.assertContains(response, "couldn")

    @override_settings(STRIPE_SECRET_KEY="sk_test_fake")
    @patch("routines.views.stripe.checkout.Session.retrieve")
    def test_checkout_success_with_bogus_session_id_does_not_crash(self, mock_retrieve):
        mock_retrieve.side_effect = stripe.error.StripeError("No such session")
        response = self.client.get(f"{reverse('checkout_success')}?session_id=cs_bogus")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["order"])

    @override_settings(STRIPE_SECRET_KEY="sk_test_fake")
    @patch("routines.views.stripe.checkout.Session.retrieve")
    def test_record_order_recovers_from_concurrent_create_race(self, mock_retrieve):
        from routines.views import _record_order_from_stripe_session

        mock_retrieve.return_value = _FakeStripeObject(
            payment_status="paid",
            amount_total=int(self.product.price * 100),
            metadata={},
            customer_details=_FakeStripeObject(email="buyer@example.com"),
        )

        # Simulate a concurrent request (webhook vs. the success-page hit)
        # having already committed the row by the time our create() runs.
        winner = Order.objects.create(
            stripe_checkout_session_id="cs_test_race",
            status=Order.Status.PAID,
            total=self.product.price,
        )

        with patch("routines.views.Order.objects.filter") as mock_filter, patch(
            "routines.views.Order.objects.create", side_effect=IntegrityError("duplicate key value")
        ):
            # Our own "does it already exist" check misses the row (that's
            # exactly what makes this a race rather than the normal path).
            mock_filter.return_value.first.return_value = None
            order = _record_order_from_stripe_session("cs_test_race")

        # Recovery falls back to a real (unpatched) Order.objects.get, which
        # finds the row the "other" request committed.
        self.assertEqual(order, winner)
        self.assertEqual(Order.objects.filter(stripe_checkout_session_id="cs_test_race").count(), 1)


class ProductDetailTests(TestCase):
    def test_product_detail_loads(self):
        product = Product.objects.filter(is_active=True).first()
        response = self.client.get(reverse("product_detail", args=[product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, product.name)

    def test_inactive_product_detail_404s(self):
        product = Product.objects.filter(is_active=True).first()
        product.is_active = False
        product.save()
        response = self.client.get(reverse("product_detail", args=[product.pk]))
        self.assertEqual(response.status_code, 404)
