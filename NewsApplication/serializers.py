"""
REST framework serializers for the NewsApplication.

Provides serializers for articles and their authors for the API feed.
"""
from rest_framework import serializers
from .models import Article, CustomUser


class AuthorSerializer(serializers.ModelSerializer):
    """Serializes a CustomUser to display username and role."""

    class Meta:
        model = CustomUser
        fields = ["username", "role"]


class ArticleSerializer(serializers.ModelSerializer):
    """Serializes an Article with nested author details."""

    independent_authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ["id", "headline", "content", "approved_status", "independent_authors"]
