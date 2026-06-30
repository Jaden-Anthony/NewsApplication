from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    TemplateView,
    UpdateView,
    DeleteView,
    View,
    DetailView,
)
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.messages.views import SuccessMessageMixin
from .models import Article, Publisher, CustomUser, Newsletter
from django.views.generic.edit import CreateView
from .forms import CustomUserRegistrationForm
from .forms import ArticleForm, PublisherStaffForm, NewsletterForm
from django.core.mail import send_mail
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import ArticleSerializer


class HomeView(ListView):
    model = Article
    template_name = "NewsApplication/index.html"
    context_object_name = "articles"

    def get_queryset(self):
        # Fetches only approved articles and orders them from newest to oldest
        return Article.objects.filter(approved_status=True).order_by("-id")


# --- Authentication Views ---


class RoleBasedLoginView(LoginView):
    # Updated to match your specific app directory
    template_name = "NewsApplication/registration/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.role == "journalist":
            return reverse_lazy("journalist_dashboard")
        elif user.role == "editor":
            return reverse_lazy("editor_dashboard")
        elif user.role == "reader":
            return reverse_lazy("article_list")
        else:
            return reverse_lazy("home")


class SignUpView(SuccessMessageMixin, CreateView):
    # 1. Tell the view which form to use
    form_class = CustomUserRegistrationForm

    # 2. Where to send the user after they successfully sign up
    success_url = reverse_lazy("home")

    # 3. The HTML template to render
    template_name = "NewsApplication/registration/register.html"
    
    success_message = "Registration successful!"


# --- Protected CRUD Views ---


class ArticleList(LoginRequiredMixin, ListView):
    model = Article
    template_name = "NewsApplication/articles/articles_list.html"
    context_object_name = "articles"

    def get_queryset(self):
        user = self.request.user

        # 1. Isolate direct Journalist subscriptions
        subscribed_journalists = user.journalist_subscriptions.all()

        # 2. Isolate Journalists belonging to subscribed Publishers
        subscribed_publishers = user.publisher_subscriptions.all()
        publisher_journalists = CustomUser.objects.filter(
            publisher_journalists__in=subscribed_publishers
        )

        # 3. Aggregate datasets using the bitwise OR operator (|) to combine querysets
        combined_author_pool = (
            subscribed_journalists | publisher_journalists
        ).distinct()

        # 4. Filter the Article database against the aggregated author pool
        return (
            Article.objects.filter(
                approved_status=True, independent_authors__in=combined_author_pool
            )
            .distinct()
            .order_by("-id")
        )


# Journalist dashboard


class JournalistDashboard(LoginRequiredMixin, TemplateView):
    template_name = "NewsApplication/dashboards/journalist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Keep the existing articles context
        context["my_articles"] = user.independent_articles.all().order_by("-id")

        # ADD the new newsletters context
        context["my_newsletters"] = user.independent_newsletters.all().order_by("-id")
        return context


# PUBLISHERS VIEWS


class PublisherListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Publisher
    template_name = "NewsApplication/publishers/publisher_list.html"
    context_object_name = "publishers"

    # Only returns True if the user is an Editor
    def test_func(self):
        return self.request.user.role == "editor"


class PublisherCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Publisher
    fields = ["name"]  # We only need the name right now
    template_name = "NewsApplication/publishers/publisher_form.html"
    success_url = reverse_lazy("manage_publishers")

    def test_func(self):
        return self.request.user.role == "editor"


class PublisherStaffManageView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Publisher
    form_class = PublisherStaffForm
    template_name = "NewsApplication/publishers/publisher_staff.html"
    success_url = reverse_lazy("manage_publishers")

    # The Bouncer
    def test_func(self):
        return self.request.user.role == "editor"


# Editor Dahsboard and CRUD views


class EditorDashboard(LoginRequiredMixin, TemplateView):
    template_name = "NewsApplication/dashboards/editor.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch ALL articles from ALL journalists where approved_status is False
        context["pending_articles"] = Article.objects.filter(
            approved_status=False
        ).order_by("id")
        return context


# The Approval Engine
class ArticleApproveView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "NewsApplication.change_article"

    def post(self, request, pk, *args, **kwargs):
        # 1. Approve the article
        article = get_object_or_404(Article, pk=pk)
        article.approved_status = True
        article.save()

        # --- EMAIL SCRIPT ---

        # Find the authors of this specific article
        authors = article.independent_authors.all()

        # Find readers subscribed directly to these authors
        journalist_subscribers = CustomUser.objects.filter(
            role="reader", journalist_subscriptions__in=authors
        )

        #  Find readers subscribed to the Publishers of these authors
        # First, get the publishers these authors belong to
        publishers = Publisher.objects.filter(journalists__in=authors)

        #  get the readers subscribed to those publishers
        publisher_subscribers = CustomUser.objects.filter(
            role="reader", publisher_subscriptions__in=publishers
        )

        # Combine the lists and remove duplicates (so no one gets two emails)
        all_subscribers = (journalist_subscribers | publisher_subscribers).distinct()

        # Extract the actual email addresses into a standard Python list
        recipient_emails = [user.email for user in all_subscribers if user.email]

        if recipient_emails:
            send_mail(
                subject=f"New Article Alert: {article.headline}",
                message=f"A new article by an author or publisher you follow has been approved!\n\nRead it now: {article.headline}\n\nSnippet: {article.content[:100]}...",
                from_email="notifications@newsapplication.com",
                recipient_list=recipient_emails,
                fail_silently=False,  # We want to see errors if it fails during testing
            )

        # --- END EMAIL AUTOMATION ---

        return redirect("editor_dashboard")


# ARTICLE CRUDS


# create article


class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "NewsApplication/articles/article_form.html"

    # The Bouncer: Only users with this specific permission can access the page
    permission_required = "NewsApplication.add_article"

    # Where to send the Journalist after they click Submit
    success_url = reverse_lazy("journalist_dashboard")

    def form_valid(self, form):
        # 1. Save the new article to the database first
        response = super().form_valid(form)

        # 2. THE MAGIC TRICK: Take the newly created article (self.object)
        # and add it to the logged-in user's 'independent_articles' list
        self.request.user.independent_articles.add(self.object)

        return response


# update article


class ArticleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm  # We reuse the exact same form from the Create step!
    template_name = (
        "NewsApplication/articles/article_form.html"  # We reuse the template too!
    )

    permission_required = "NewsApplication.change_article"
    success_url = reverse_lazy("journalist_dashboard")

    def get_queryset(self):
        # SECURITY: Restrict the query so they can only edit their own work
        return self.request.user.independent_articles.all()


# delete article


class ArticleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Article
    template_name = "NewsApplication/articles/article_confirm_delete.html"

    permission_required = "NewsApplication.delete_article"
    success_url = reverse_lazy("journalist_dashboard")

    def get_queryset(self):
        # SECURITY: Restrict the query so they can only delete their own work
        return self.request.user.independent_articles.all()


# view article details


class ArticleDetailView(DetailView):
    model = Article
    template_name = "NewsApplication/articles/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        """
        SECURITY:
        - Editors can view ALL articles (so they can review drafts).
        - Journalists can view ALL articles (so they can read their own drafts).
        - Readers & Anonymous users can ONLY view approved articles.
        """
        user = self.request.user
        if user.is_authenticated and user.role in ["editor", "journalist"]:
            return Article.objects.all()

        # If they aren't an editor or journalist, lock it down to approved only
        return Article.objects.filter(approved_status=True)


# subscription logic


class ToggleJournalistSubscription(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        # 1. Find the journalist the reader is trying to subscribe to
        journalist = get_object_or_404(CustomUser, pk=pk, role="journalist")
        reader = request.user

        # 2. Only Readers should be subscribing to things
        if reader.role == "reader":
            # 3. Toggle Logic: Add or Remove
            if journalist in reader.journalist_subscriptions.all():
                reader.journalist_subscriptions.remove(journalist)
            else:
                reader.journalist_subscriptions.add(journalist)

        # 4. Redirect them right back to the page they were just looking at
        return redirect(request.META.get("HTTP_REFERER", "home"))


class TogglePublisherSubscription(LoginRequiredMixin, View):
    """Handles the addition and removal of Publisher entities from the Reader's relational mapping."""

    def post(self, request, pk, *args, **kwargs):
        publisher = get_object_or_404(Publisher, pk=pk)
        reader = request.user

        if reader.role == "reader":
            if publisher in reader.publisher_subscriptions.all():
                reader.publisher_subscriptions.remove(publisher)
            else:
                reader.publisher_subscriptions.add(publisher)

        return redirect(request.META.get("HTTP_REFERER", "home"))


class ReaderSubscriptionsView(LoginRequiredMixin, TemplateView):
    template_name = "NewsApplication/reader/subscriptions_manage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Datasets for currently active subscriptions
        context["journalists"] = user.journalist_subscriptions.all()
        context["publishers"] = user.publisher_subscriptions.all()

        # Dataset for discovery (Publishers the user is not currently following)
        context["available_publishers"] = Publisher.objects.exclude(subscribers=user)

        return context


#  Newsletter CRUD Views
class NewsletterCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "NewsApplication/newsletters/newsletter_form.html"
    permission_required = "NewsApplication.add_newsletter"
    success_url = reverse_lazy("journalist_dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        # THE MAGIC TRICK: Link it to the Journalist's specific field
        self.request.user.independent_newsletters.add(self.object)
        return response


class NewsletterUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "NewsApplication/newsletters/newsletter_form.html"
    permission_required = "NewsApplication.change_newsletter"
    success_url = reverse_lazy("journalist_dashboard")

    def get_queryset(self):
        # SECURITY: Only let them edit their own newsletters
        return self.request.user.independent_newsletters.all()


class NewsletterDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Newsletter
    template_name = "NewsApplication/newsletters/newsletter_confirm_delete.html"
    permission_required = "NewsApplication.delete_newsletter"
    success_url = reverse_lazy("journalist_dashboard")

    def get_queryset(self):
        # SECURITY: Only let them delete their own newsletters
        return self.request.user.independent_newsletters.all()


class ReaderNewsletterList(LoginRequiredMixin, ListView):
    model = Newsletter
    template_name = "NewsApplication/newsletters/reader_newsletter_list.html"
    context_object_name = "newsletters"

    def get_queryset(self):
        user = self.request.user
        if user.role == "reader":
            # Retrieve journalists the reader follows
            subscribed_journalists = user.journalist_subscriptions.all()

            # Since CustomUser has a ManyToMany to Newsletter, we query backward
            # Assuming default reverse relation if related_name wasn't set, usually user_set or customuser_set
            return (
                Newsletter.objects.filter(
                    independent_authors__in=subscribed_journalists
                )
                .distinct()
                .order_by("-id")
            )
        return Newsletter.objects.none()


# $API VIEWS


class SubscribedArticleFeedAPI(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 1. Isolate direct Journalist subscriptions
        subscribed_journalists = user.journalist_subscriptions.all()

        # 2. Isolate Journalists belonging to subscribed Publishers
        subscribed_publishers = user.publisher_subscriptions.all()
        publisher_journalists = CustomUser.objects.filter(
            publisher_journalists__in=subscribed_publishers
        )

        # 3. Aggregate datasets using bitwise OR
        combined_author_pool = (
            subscribed_journalists | publisher_journalists
        ).distinct()

        # 4. Return serialized filtered dataset
        return (
            Article.objects.filter(
                approved_status=True, independent_authors__in=combined_author_pool
            )
            .distinct()
            .order_by("-id")
        )
