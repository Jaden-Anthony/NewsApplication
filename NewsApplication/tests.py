from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser, Article, Newsletter, Publisher

# ──────────────────────────────────────────────────────────────────────────────
# Model Tests
# ──────────────────────────────────────────────────────────────────────────────


class ArticleModelTest(TestCase):
    def test_str_returns_headline(self):
        article = Article.objects.create(
            headline="Test Headline", content="Some content"
        )
        self.assertEqual(str(article), "Test Headline")

    def test_default_approved_status_is_false(self):
        article = Article.objects.create(headline="Draft", content="...")
        self.assertFalse(article.approved_status)


class NewsletterModelTest(TestCase):
    def test_str_returns_title(self):
        nl = Newsletter.objects.create(title="Weekly Brief", content="...")
        self.assertEqual(str(nl), "Weekly Brief")


class PublisherModelTest(TestCase):
    def test_str_returns_name(self):
        pub = Publisher.objects.create(name="Daily Times")
        self.assertEqual(str(pub), "Daily Times")


class CustomUserRoleTest(TestCase):
    def test_reader_role_default(self):
        user = CustomUser.objects.create_user(username="reader1", password="pass123")
        self.assertEqual(user.role, "reader")

    def test_journalist_clear_reader_fields(self):
        journalist = CustomUser.objects.create_user(
            username="journo1", password="pass123", role="journalist"
        )
        pub = Publisher.objects.create(name="Pub A")
        journalist.publisher_subscriptions.add(pub)
        journalist.save()
        self.assertEqual(journalist.publisher_subscriptions.count(), 0)

    def test_reader_clear_journalist_fields(self):
        reader = CustomUser.objects.create_user(
            username="reader2", password="pass123", role="reader"
        )
        article = Article.objects.create(headline="Headline", content="Body")
        reader.independent_articles.add(article)
        reader.save()
        self.assertEqual(reader.independent_articles.count(), 0)


# ──────────────────────────────────────────────────────────────────────────────
# View Tests
# ──────────────────────────────────────────────────────────────────────────────


class HomeViewTest(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_uses_correct_template(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "NewsApplication/index.html")

    def test_home_only_shows_approved_articles(self):
        Article.objects.create(headline="Approved", content="...", approved_status=True)
        Article.objects.create(headline="Draft", content="...", approved_status=False)
        response = self.client.get(reverse("home"))
        articles = response.context["articles"]
        self.assertEqual(articles.count(), 1)
        self.assertEqual(articles.first().headline, "Approved")


class LoginViewTest(TestCase):
    def test_login_page_returns_200(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_uses_correct_template(self):
        response = self.client.get(reverse("login"))
        self.assertTemplateUsed(response, "NewsApplication/registration/login.html")

    def test_invalid_login_stays_on_login_page(self):
        response = self.client.post(
            reverse("login"), {"username": "nobody", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)


class RoleBasedLoginRedirectTest(TestCase):
    def setUp(self):
        self.journalist = CustomUser.objects.create_user(
            username="j_user", password="pass123", role="journalist"
        )
        self.editor = CustomUser.objects.create_user(
            username="e_user", password="pass123", role="editor"
        )
        self.reader = CustomUser.objects.create_user(
            username="r_user", password="pass123", role="reader"
        )

    def test_journalist_redirected_to_dashboard(self):
        response = self.client.post(
            reverse("login"), {"username": "j_user", "password": "pass123"}
        )
        self.assertRedirects(response, reverse("journalist_dashboard"))

    def test_editor_redirected_to_dashboard(self):
        response = self.client.post(
            reverse("login"), {"username": "e_user", "password": "pass123"}
        )
        self.assertRedirects(response, reverse("editor_dashboard"))

    def test_reader_redirected_to_article_list(self):
        response = self.client.post(
            reverse("login"), {"username": "r_user", "password": "pass123"}
        )
        self.assertRedirects(response, reverse("article_list"))


class SignUpViewTest(TestCase):
    def test_register_page_returns_200(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_register_page_uses_correct_template(self):
        response = self.client.get(reverse("register"))
        self.assertTemplateUsed(response, "NewsApplication/registration/register.html")

    def test_successful_registration_redirects_to_home(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "Str0ng!Pass99",
                "password2": "Str0ng!Pass99",
                "role": "reader",
            },
        )
        self.assertRedirects(response, reverse("home"))

    def test_successful_registration_creates_user(self):
        self.client.post(
            reverse("register"),
            {
                "username": "brandnewuser",
                "password1": "Str0ng!Pass99",
                "password2": "Str0ng!Pass99",
                "role": "reader",
            },
        )
        self.assertTrue(CustomUser.objects.filter(username="brandnewuser").exists())

    def test_mismatched_passwords_stays_on_register(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "failuser",
                "password1": "Str0ng!Pass99",
                "password2": "differentpass",
                "role": "reader",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_duplicate_username_stays_on_register(self):
        CustomUser.objects.create_user(username="taken", password="pass123")
        response = self.client.post(
            reverse("register"),
            {
                "username": "taken",
                "password1": "Str0ng!Pass99",
                "password2": "Str0ng!Pass99",
                "role": "reader",
            },
        )
        self.assertEqual(response.status_code, 200)


class JournalistDashboardTest(TestCase):
    def setUp(self):
        self.journalist = CustomUser.objects.create_user(
            username="journo", password="pass123", role="journalist"
        )
        self.client.login(username="journo", password="pass123")

    def test_dashboard_accessible_to_journalist(self):
        response = self.client.get(reverse("journalist_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirects_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse("journalist_dashboard"))
        self.assertEqual(response.status_code, 302)


class EditorDashboardTest(TestCase):
    def setUp(self):
        self.editor = CustomUser.objects.create_user(
            username="editor1", password="pass123", role="editor"
        )
        self.client.login(username="editor1", password="pass123")

    def test_editor_dashboard_accessible(self):
        response = self.client.get(reverse("editor_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_pending_articles_appear_in_context(self):
        Article.objects.create(headline="Pending", content="...", approved_status=False)
        response = self.client.get(reverse("editor_dashboard"))
        self.assertIn("pending_articles", response.context)
        self.assertEqual(response.context["pending_articles"].count(), 1)


class ArticleApproveTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        self.editor = CustomUser.objects.create_user(
            username="approver", password="pass123", role="editor"
        )
        ct = ContentType.objects.get_for_model(Article)
        perm = Permission.objects.get(codename="change_article", content_type=ct)
        self.editor.user_permissions.add(perm)

        self.article = Article.objects.create(
            headline="Needs Approval", content="...", approved_status=False
        )
        self.client.login(username="approver", password="pass123")

    def test_approve_sets_approved_status(self):
        self.client.post(reverse("article_approve", kwargs={"pk": self.article.pk}))
        self.article.refresh_from_db()
        self.assertTrue(self.article.approved_status)

    def test_unauthenticated_cannot_approve(self):
        self.client.logout()
        response = self.client.post(
            reverse("article_approve", kwargs={"pk": self.article.pk})
        )
        # should redirect to login, not 200
        self.assertNotEqual(response.status_code, 200)


class ReaderFeedTest(TestCase):
    def setUp(self):
        self.reader = CustomUser.objects.create_user(
            username="reader_feed", password="pass123", role="reader"
        )
        self.journalist = CustomUser.objects.create_user(
            username="journo_feed", password="pass123", role="journalist"
        )
        self.article = Article.objects.create(
            headline="Sub Article", content="...", approved_status=True
        )
        self.journalist.independent_articles.add(self.article)
        self.reader.journalist_subscriptions.add(self.journalist)
        self.client.login(username="reader_feed", password="pass123")

    def test_reader_sees_subscribed_article(self):
        response = self.client.get(reverse("article_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.article, response.context["articles"])

    def test_reader_does_not_see_unsubscribed_article(self):
        other_journo = CustomUser.objects.create_user(
            username="other_j", password="pass123", role="journalist"
        )
        other_article = Article.objects.create(
            headline="Unsubbed", content="...", approved_status=True
        )
        other_journo.independent_articles.add(other_article)
        response = self.client.get(reverse("article_list"))
        self.assertNotIn(other_article, response.context["articles"])


# ──────────────────────────────────────────────────────────────────────────────
# REST API Tests
# ──────────────────────────────────────────────────────────────────────────────


class ArticleAPITests(APITestCase):
    def setUp(self):
        self.reader = CustomUser.objects.create_user(
            username="api_reader", password="testpassword", role="reader"
        )
        self.subscribed_journo = CustomUser.objects.create_user(
            username="subbed_j", password="testpassword", role="journalist"
        )
        self.unsubscribed_journo = CustomUser.objects.create_user(
            username="unsubbed_j", password="testpassword", role="journalist"
        )
        self.article1 = Article.objects.create(
            headline="Subbed Article", content="Test", approved_status=True
        )
        self.subscribed_journo.independent_articles.add(self.article1)

        self.article2 = Article.objects.create(
            headline="Unsubbed Article", content="Test", approved_status=True
        )
        self.unsubscribed_journo.independent_articles.add(self.article2)

        self.reader.journalist_subscriptions.add(self.subscribed_journo)

    def test_subscribed_feed_retrieval(self):
        self.client.login(username="api_reader", password="testpassword")
        response = self.client.get("/api/feed/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["headline"], "Subbed Article")

    def test_unauthenticated_feed_returns_401(self):
        response = self.client.get("/api/feed/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_feed_excludes_unapproved_articles(self):
        unapproved = Article.objects.create(
            headline="Not Approved", content="...", approved_status=False
        )
        self.subscribed_journo.independent_articles.add(unapproved)
        self.client.login(username="api_reader", password="testpassword")
        response = self.client.get("/api/feed/")
        headlines = [a["headline"] for a in response.data]
        self.assertNotIn("Not Approved", headlines)
