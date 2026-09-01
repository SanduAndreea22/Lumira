import logging
from decimal import ROUND_HALF_UP, Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .. import cart as cart_utils
from ..models import Order, OrderItem, Product

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def _to_cents(price: Decimal) -> int:
    """Round (not truncate) a Decimal price to integer cents for Stripe."""
    return int((price * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@require_POST
def checkout(request):
    items = cart_utils.get_items(request)
    if not items:
        return redirect("cart_view")
    if not settings.STRIPE_SECRET_KEY:
        messages.error(
            request,
            "Checkout isn't configured yet — this demo needs Stripe test-mode API keys.",
        )
        return redirect("cart_view")

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": item["product"].name,
                            "metadata": {"lumira_product_id": str(item["product"].pk)},
                        },
                        "unit_amount": _to_cents(item["product"].price),
                    },
                    "quantity": item["quantity"],
                }
                for item in items
            ],
            customer_email=request.user.email
            if request.user.is_authenticated and request.user.email
            else None,
            metadata={"user_id": str(request.user.pk) if request.user.is_authenticated else ""},
            success_url=request.build_absolute_uri(reverse("checkout_success"))
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("checkout_cancel")),
        )
    except stripe.error.StripeError:
        logger.exception("Stripe checkout session creation failed")
        messages.error(request, "We couldn't start checkout — please try again in a moment.")
        return redirect("cart_view")
    return redirect(session.url)


def _record_order_from_stripe_session(session_id):
    """Idempotently turn a completed Stripe Checkout Session into an Order.

    Reads everything it needs back from Stripe (not the Django session), so
    it works the same whether it's called from the webhook (no session
    access at all) or from the success-page fallback — both call this, and
    can race each other, which is why the create below is guarded against
    a duplicate stripe_checkout_session_id rather than assuming the earlier
    existence check was the last word.

    Returns None if the session doesn't exist, isn't paid, or Stripe
    couldn't be reached — callers treat that as "not confirmed (yet)"
    rather than an error.
    """
    existing = Order.objects.filter(stripe_checkout_session_id=session_id).first()
    if existing:
        return existing

    try:
        stripe_session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        logger.exception("Failed to retrieve Stripe session %s", session_id)
        return None

    if stripe_session.payment_status != "paid":
        return None

    try:
        with transaction.atomic():
            order = Order.objects.create(
                stripe_checkout_session_id=session_id,
                user_id=(stripe_session.metadata or {}).get("user_id") or None,
                email=(stripe_session.customer_details.email if stripe_session.customer_details else "")
                or "",
                status=Order.Status.PAID,
                total=Decimal(stripe_session.amount_total) / 100,
            )
    except IntegrityError:
        # Lost the race to a concurrent call (webhook vs. success page).
        return Order.objects.get(stripe_checkout_session_id=session_id)

    try:
        line_items = stripe.checkout.Session.list_line_items(
            session_id, expand=["data.price.product"], limit=100
        )
    except stripe.error.StripeError:
        logger.exception("Order %s created but failed to fetch its line items", order.pk)
        return order

    for line_item in line_items.data:
        product_id = line_item.price.product.metadata.get("lumira_product_id")
        product = Product.objects.filter(pk=product_id).first()
        if product:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=line_item.quantity,
                unit_price=Decimal(line_item.price.unit_amount) / 100,
            )
        else:
            # Paid for, but the product no longer exists in our catalog —
            # don't drop this silently, someone needs to reconcile it.
            logger.error(
                "Order %s: paid line item references missing product_id=%s (%s x %s)",
                order.pk,
                product_id,
                line_item.quantity,
                line_item.price.unit_amount,
            )
    return order


def checkout_success(request):
    session_id = request.GET.get("session_id")
    order = None
    if session_id and settings.STRIPE_SECRET_KEY:
        order = _record_order_from_stripe_session(session_id)
    if order:
        cart_utils.clear(request)
    return render(request, "routines/checkout_success.html", {"order": order})


def checkout_cancel(request):
    return render(request, "routines/checkout_cancel.html")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponseBadRequest("Webhook not configured")
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.META.get("HTTP_STRIPE_SIGNATURE", ""),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest("Invalid signature")

    if event["type"] == "checkout.session.completed":
        order = _record_order_from_stripe_session(event["data"]["object"]["id"])
        if order is None:
            # Couldn't confirm/record this one (Stripe was unreachable, most
            # likely) — a non-2xx tells Stripe to retry the webhook later.
            return HttpResponse(status=502)

    return HttpResponse(status=200)
