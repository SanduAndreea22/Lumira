import logging

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from ..diagnostics import NoProductAvailable, build_routine
from ..forms import ConcernStepForm, ExperienceStepForm, PreferencesStepForm, SkinTypeStepForm
from ..models import Concern, DiagnosticResult, SkinType

logger = logging.getLogger(__name__)

SESSION_KEY = "diagnostic_answers"

STEPS = [
    ("concern", ConcernStepForm, "What's bothering you the most right now?"),
    ("skin_type", SkinTypeStepForm, "What's your skin type?"),
    ("experience", ExperienceStepForm, "How experienced are you with skincare?"),
    ("preferences", PreferencesStepForm, "Any preferences? (optional)"),
]


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

    try:
        steps = build_routine(result, save=False)
    except NoProductAvailable:
        logger.exception(
            "No product available for concern=%s skin_type=%s", result.concern_id, result.skin_type_id
        )
        messages.error(
            request,
            "We couldn't build a full routine for that combination right now — please try again shortly.",
        )
        return redirect("home")

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


def _do_save_routine(request):
    """Save the session's diagnostic result as a Routine for request.user
    and return the redirect to send them to. Assumes request.user is
    authenticated — callers (save_routine, signup) check that first.
    """
    result = _result_from_session(request)
    if result is None:
        return redirect("diagnostic_step", step_number=1)

    result.user = request.user
    result.save()
    try:
        build_routine(result, user=request.user, save=True)
    except NoProductAvailable:
        logger.exception(
            "No product available for concern=%s skin_type=%s", result.concern_id, result.skin_type_id
        )
        messages.error(
            request,
            "We couldn't build a full routine for that combination right now — please try again shortly.",
        )
        return redirect("routine_result")
    del request.session[SESSION_KEY]
    messages.success(request, "Your routine is saved to your account.")
    return redirect("my_routines")


@require_POST
def save_routine(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('signup')}?next={reverse('save_routine')}")
    return _do_save_routine(request)


@require_POST
def redo_diagnostic(request):
    request.session.pop(SESSION_KEY, None)
    return redirect("diagnostic_step", step_number=1)
