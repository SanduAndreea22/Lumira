import logging
import time

from django.contrib import messages
from django.shortcuts import redirect, render

from ..forms import ContactForm
from ..models import Concern

logger = logging.getLogger(__name__)

CONTACT_THROTTLE_SECONDS = 30


def home(request):
    return render(request, "routines/home.html", {"concerns": Concern.objects.all()})


def about(request):
    return render(request, "routines/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            success_message = "Thanks for reaching out — we'll get back to you within 1-2 business days."
            if form.is_spam():
                # Don't tip off the bot — just pretend it worked.
                messages.success(request, success_message)
                return redirect("contact")

            last_submitted = request.session.get("last_contact_submission", 0)
            if time.time() - last_submitted < CONTACT_THROTTLE_SECONDS:
                messages.error(request, "You're sending messages too quickly — please wait a moment and try again.")
                return redirect("contact")

            form.save()
            request.session["last_contact_submission"] = time.time()
            messages.success(request, success_message)
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "routines/contact.html", {"form": form})
