from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from .models import Article, Publisher, Newsletter


class CustomUserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        # We explicitly list the fields we want the user to fill out
        fields = ("username", "email", "role")


# create article form


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article

        fields = ["headline", "content"]


# newsletter


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ["title", "content"]


# publisher form


class PublisherStaffForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ["journalists"]  # We are only editing the journalists list

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. Filter the list so it ONLY shows users with the 'journalist' role
        self.fields["journalists"].queryset = CustomUser.objects.filter(
            role="journalist"
        )

        # 2. Make the UI a list of checkboxes instead of an ugly multi-select box
        self.fields["journalists"].widget = forms.CheckboxSelectMultiple()
