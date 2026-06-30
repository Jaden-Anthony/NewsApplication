from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    # Authentication Routes
    path("login/", views.RoleBasedLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.SignUpView.as_view(), name="register"),
    # CRUD Routes
    path("articles/", views.ArticleList.as_view(), name="article_list"),
    # Dashboard Routes
    path(
        "journalist/dashboard/",
        views.JournalistDashboard.as_view(),
        name="journalist_dashboard",
    ),
    path("editor/dashboard/", views.EditorDashboard.as_view(), name="editor_dashboard"),
    path("articles/new/", views.ArticleCreateView.as_view(), name="article_create"),
    path(
        "articles/<int:pk>/edit/",
        views.ArticleUpdateView.as_view(),
        name="article_edit",
    ),
    path(
        "articles/<int:pk>/delete/",
        views.ArticleDeleteView.as_view(),
        name="article_delete",
    ),
    path(
        "editor/article/<int:pk>/approve/",
        views.ArticleApproveView.as_view(),
        name="article_approve",
    ),
    path(
        "articles/<int:pk>/", views.ArticleDetailView.as_view(), name="article_detail"
    ),
    path(
        "editor/publishers/",
        views.PublisherListView.as_view(),
        name="manage_publishers",
    ),
    path(
        "editor/publishers/new/",
        views.PublisherCreateView.as_view(),
        name="publisher_create",
    ),
    path(
        "editor/publishers/<int:pk>/staff/",
        views.PublisherStaffManageView.as_view(),
        name="publisher_staff",
    ),
    path(
        "subscribe/journalist/<int:pk>/",
        views.ToggleJournalistSubscription.as_view(),
        name="toggle_journalist_sub",
    ),
    path(
        "subscribe/publisher/<int:pk>/",
        views.TogglePublisherSubscription.as_view(),
        name="toggle_publisher_sub",
    ),
    path(
        "subscriptions/",
        views.ReaderSubscriptionsView.as_view(),
        name="manage_subscriptions",
    ),
    # Newsletter CRUD Routes
    path(
        "newsletters/new/",
        views.NewsletterCreateView.as_view(),
        name="newsletter_create",
    ),
    path(
        "newsletters/<int:pk>/edit/",
        views.NewsletterUpdateView.as_view(),
        name="newsletter_edit",
    ),
    path(
        "newsletters/<int:pk>/delete/",
        views.NewsletterDeleteView.as_view(),
        name="newsletter_delete",
    ),
    path(
        "my-newsletters/",
        views.ReaderNewsletterList.as_view(),
        name="reader_newsletters",
    ),
    path("api/feed/", views.SubscribedArticleFeedAPI.as_view(), name="api_feed"),
]
