from django.test import TestCase

# Create your tests here.

from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser, Article


class ArticleAPITests(APITestCase):
    def setUp(self):
        # 1. Create a Reader
        self.reader = CustomUser.objects.create_user(
            username="api_reader", password="testpassword", role="reader"
        )

        # 2. Create two Journalists
        self.subscribed_journo = CustomUser.objects.create_user(
            username="subbed_j", password="testpassword", role="journalist"
        )
        self.unsubscribed_journo = CustomUser.objects.create_user(
            username="unsubbed_j", password="testpassword", role="journalist"
        )

        # 3. Create Articles
        self.article1 = Article.objects.create(
            headline="Subbed Article", content="Test", approved_status=True
        )
        self.subscribed_journo.independent_articles.add(self.article1)

        self.article2 = Article.objects.create(
            headline="Unsubbed Article", content="Test", approved_status=True
        )
        self.unsubscribed_journo.independent_articles.add(self.article2)

        # 4. Establish Subscription
        self.reader.journalist_subscriptions.add(self.subscribed_journo)

    def test_subscribed_feed_retrieval(self):
        """
        Ensure the API only returns articles from subscribed journalists.
        """
        # Authenticate the test client
        self.client.login(username="api_reader", password="testpassword")

        # Execute GET request
        response = self.client.get("/api/feed/")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["headline"], "Subbed Article")
