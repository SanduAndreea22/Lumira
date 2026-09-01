import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .. import cart as cart_utils
from ..diagnostics import NoProductAvailable, build_routine
from ..models import Product
from .quiz import _result_from_session

logger = logging.getLogger(__name__)


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
        return redirect("routine_result")
    for step in steps:
        cart_utils.add(request, step.product.pk)
    messages.success(request, "Your routine's products were added to your cart.")
    return redirect("cart_view")


def cart_view(request):
    items = cart_utils.get_items(request)
    total = cart_utils.get_total(request)
    return render(request, "routines/cart.html", {"items": items, "total": total})
