from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Concern, ContactMessage, DiagnosticResult, SkinType


class ConcernStepForm(forms.Form):
    concern = forms.ModelChoiceField(
        queryset=Concern.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
    )


class SkinTypeStepForm(forms.Form):
    skin_type = forms.ModelChoiceField(
        queryset=SkinType.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
    )


class ExperienceStepForm(forms.Form):
    experience = forms.ChoiceField(
        choices=DiagnosticResult.Experience.choices,
        widget=forms.RadioSelect,
    )


class PreferencesStepForm(forms.Form):
    fragrance_free = forms.BooleanField(label="Fragrance-free only", required=False)
    vegan = forms.BooleanField(label="Vegan only", required=False)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("subject", "name", "email", "message")
        widgets = {
            "subject": forms.RadioSelect,
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].initial = ContactMessage.Subject.OTHER
