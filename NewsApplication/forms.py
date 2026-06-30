"""
Forms for the NewsApplication.

Provides custom forms for user registration, article creation,
newsletter management, and publisher staff assignment.
"""
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from .models import Article, Publisher, Newsletter


class CustomUserRegistrationForm(UserCreationForm):
    """Registration form that includes username, email, and role selection."""

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role")


class ArticleForm(forms.ModelForm):
    """Form for creating and editing articles."""

    class Meta:
        model = Article
        fields = ["headline", "content"]


class NewsletterForm(forms.ModelForm):
    """Form for creating and editing newsletters."""

    class Meta:
        model = Newsletter
        fields = ["title", "content"]


class PublisherStaffForm(forms.ModelForm):
    """Form for managing which journalists belong to a publisher."""

    class Meta:
        model = Publisher
        fields = ["journalists"]

    def __init__(self, *args, **kwargs):
        """Filter the journalists field to only show users with the journalist role."""
        super().__init__(*args, **kwargs)
        self.fields["journalists"].queryset = CustomUser.objects.filter(
            role="journalist"
        )
        self.fields["journalists"].widget = forms.CheckboxSelectMultiple()
