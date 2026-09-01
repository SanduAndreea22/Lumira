from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .diagnostics import build_routine
from .forms import (
    ConcernStepForm,
    ContactForm,
    ExperienceStepForm,
    PreferencesStepForm,
    SignUpForm,
    SkinTypeStepForm,
)
from .models import Concern, DiagnosticResult, Product, Routine, SkinType

SESSION_KEY = "diagnostic_answers"

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

    return render(
        request,
        "routines/diagnostic_step.html",
        {
            "form": form,
            "question": question,
            "step_number": step_number,
            "total_steps": len(STEPS),
            "progress_pct": int(step_number / len(STEPS) * 100),
        },
    )


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
