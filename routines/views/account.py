from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from ..forms import SignUpForm
from ..models import Routine
from .quiz import _do_save_routine


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
            if next_url == reverse("save_routine"):
                # save_routine is POST-only; do the save directly instead
                # of redirecting into a GET on that URL.
                return _do_save_routine(request)
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
