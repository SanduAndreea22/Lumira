from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import cart as cart_utils
from .diagnostics import build_routine
from .forms import (
    ConcernStepForm,
    ContactForm,
    ExperienceStepForm,
    PreferencesStepForm,
    SignUpForm,
    SkinTypeStepForm,
)
from .models import Concern, DiagnosticResult, Order, OrderItem, Product, Routine, SkinType

SESSION_KEY = "diagnostic_answers"

stripe.api_key = settings.STRIPE_SECRET_KEY

STEPS = [
    ("concern", ConcernStepForm, "What's bothering you the most right now?"),
    ("skin_type", SkinTypeStepForm, "What's your skin type?"),
    ("experience", ExperienceStepForm, "How experienced are you with skincare?"),
    ("preferences", PreferencesStepForm, "Any preferences? (optional)"),
]


def home(request):
    return render(request, "routines/home.html", {"concerns": Concern.objects.all()})


def diagnostic_step(request, step_number):
    step_number = int(step_number)
    if step_number < 1 or step_number > len(STEPS):
        return redirect("diagnostic_step", step_number=1)

    field_name, form_class, question = STEPS[step_number - 1]
    answers = request.session.get(SESSION_KEY, {})

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            for key, value in form.cleaned_data.items():
                answers[key] = value.pk if hasattr(value, "pk") else value
            request.session[SESSION_KEY] = answers
            if step_number == len(STEPS):
                return redirect("routine_result")
            return redirect("diagnostic_step", step_number=step_number + 1)
    else:
        initial = {}
        if field_name == "preferences":
            initial = {
                "fragrance_free": answers.get("fragrance_free", False),
                "vegan": answers.get("vegan", False),
            }
        elif field_name in answers:
            initial = {field_name: answers[field_name]}
        form = form_class(initial=initial)

    context = {
        "form": form,
        "field_name": field_name,
        "question": question,
        "step_number": step_number,
        "total_steps": len(STEPS),
        "progress_pct": int(step_number / len(STEPS) * 100),
    }
    if field_name == "concern":
        context["concern_icons"] = {str(c.pk): c.icon for c in Concern.objects.all()}
    return render(request, "routines/diagnostic_step.html", context)


def _result_from_session(request):
    answers = request.session.get(SESSION_KEY)
    if not answers or "concern" not in answers or "skin_type" not in answers:
        return None
    try:
        concern = Concern.objects.get(pk=answers["concern"])
        skin_type = SkinType.objects.get(pk=answers["skin_type"])
    except (Concern.DoesNotExist, SkinType.DoesNotExist):
        return None
    return DiagnosticResult(
        concern=concern,
        skin_type=skin_type,
        experience=answers.get("experience", DiagnosticResult.Experience.SOME_ROUTINE),
        wants_fragrance_free=answers.get("fragrance_free", False),
        wants_vegan=answers.get("vegan", False),
    )


def routine_result(request):
    result = _result_from_session(request)
    if result is None:
        messages.info(request, "Let's start with a couple of quick questions first.")
        return redirect("diagnostic_step", step_number=1)

    steps = build_routine(result, save=False)
    am_steps = [s for s in steps if s.time_of_day == "am"]
    pm_steps = [s for s in steps if s.time_of_day == "pm"]

    return render(
        request,
        "routines/routine_result.html",
        {
            "result": result,
            "am_steps": am_steps,
            "pm_steps": pm_steps,
        },
    )


def save_routine(request):
    result = _result_from_session(request)
    if result is None:
        return redirect("diagnostic_step", step_number=1)

    if not request.user.is_authenticated:
        return redirect(f"{reverse('signup')}?next={reverse('save_routine')}")

    result.user = request.user
    result.save()
    build_routine(result, user=request.user, save=True)
    del request.session[SESSION_KEY]
    messages.success(request, "Your routine is saved to your account.")
    return redirect("my_routines")


def signup(request):
    next_param = request.GET.get("next") or request.POST.get("next") or ""
    if url_has_allowed_host_and_scheme(
        next_param, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = next_param
    else:
        next_url = "home"
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(next_url)
    else:
        form = SignUpForm()
    return render(request, "routines/signup.html", {"form": form, "next": next_url})


@login_required
def my_routines(request):
    routines = request.user.routines.prefetch_related("steps__product", "diagnostic_result__concern")
    return render(request, "routines/my_routines.html", {"routines": routines})


@login_required
def routine_detail(request, pk):
    routine = get_object_or_404(
        Routine.objects.prefetch_related("steps__product"), pk=pk, user=request.user
    )
    am_steps = routine.steps.filter(time_of_day="am")
    pm_steps = routine.steps.filter(time_of_day="pm")
    return render(
        request,
        "routines/routine_detail.html",
        {"routine": routine, "am_steps": am_steps, "pm_steps": pm_steps},
    )


def redo_diagnostic(request):
    request.session.pop(SESSION_KEY, None)
    return redirect("diagnostic_step", step_number=1)


def about(request):
    return render(request, "routines/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Thanks for reaching out — we'll get back to you within 1-2 business days."
            )
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "routines/contact.html", {"form": form})


def _safe_next(request, fallback):
    next_param = request.POST.get("next") or request.GET.get("next") or ""
    if url_has_allowed_host_and_scheme(
        next_param, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return next_param
    return fallback


@require_POST
def add_to_cart(request, pk):
    get_object_or_404(Product, pk=pk, is_active=True)
    cart_utils.add(request, pk)
    messages.success(request, "Added to your cart.")
    return redirect(_safe_next(request, reverse("cart_view")))


@require_POST
def remove_from_cart_view(request, pk):
    cart_utils.remove(request, pk)
    return redirect("cart_view")


@require_POST
def add_routine_to_cart(request):
    result = _result_from_session(request)
    if result is None:
        return redirect("diagnostic_step", step_number=1)
    for step in build_routine(result, save=False):
        cart_utils.add(request, step.product.pk)
    messages.success(request, "Your routine's products were added to your cart.")
    return redirect("cart_view")


def cart_view(request):
    items = cart_utils.get_items(request)
    total = cart_utils.get_total(request)
    return render(request, "routines/cart.html", {"items": items, "total": total})


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
                    "unit_amount": int(item["product"].price * 100),
                },
                "quantity": item["quantity"],
            }
            for item in items
        ],
        customer_email=request.user.email if request.user.is_authenticated and request.user.email else None,
        metadata={"user_id": str(request.user.pk) if request.user.is_authenticated else ""},
        success_url=request.build_absolute_uri(reverse("checkout_success"))
        + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse("checkout_cancel")),
    )
    return redirect(session.url)


def _record_order_from_stripe_session(session_id):
    """Idempotently turn a completed Stripe Checkout Session into an Order.

    Reads everything it needs back from Stripe (not the Django session), so
    it works the same whether it's called from the webhook (no session
    access at all) or from the success-page fallback.
    """
    existing = Order.objects.filter(stripe_checkout_session_id=session_id).first()
    if existing:
        return existing

    stripe_session = stripe.checkout.Session.retrieve(session_id)
    if stripe_session.payment_status != "paid":
        return None

    order = Order.objects.create(
        stripe_checkout_session_id=session_id,
        user_id=(stripe_session.metadata or {}).get("user_id") or None,
        email=(stripe_session.customer_details.email if stripe_session.customer_details else "") or "",
        status=Order.Status.PAID,
        total=Decimal(stripe_session.amount_total) / 100,
    )
    line_items = stripe.checkout.Session.list_line_items(
        session_id, expand=["data.price.product"], limit=100
    )
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
        _record_order_from_stripe_session(event["data"]["object"]["id"])

    return HttpResponse(status=200)


def product_catalog(request):
    products = Product.objects.filter(is_active=True).prefetch_related("concerns", "skin_types")
    concern_slug = request.GET.get("concern") or ""
    skin_slug = request.GET.get("skin_type") or ""
    if concern_slug:
        products = products.filter(concerns__slug=concern_slug)
    if skin_slug:
        products = products.filter(skin_types__slug=skin_slug)
    return render(
        request,
        "routines/products.html",
        {
            "products": products.distinct(),
            "concerns": Concern.objects.all(),
            "skin_types": SkinType.objects.all(),
            "selected_concern": concern_slug,
            "selected_skin_type": skin_slug,
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related("concerns", "skin_types"), pk=pk, is_active=True
    )
    return render(request, "routines/product_detail.html", {"product": product})
