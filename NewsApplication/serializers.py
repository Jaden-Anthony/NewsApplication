from rest_framework import serializers
from .models import Article, CustomUser


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "role"]


class ArticleSerializer(serializers.ModelSerializer):
    # Nested serializer to display author details instead of just primary keys
    independent_authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ["id", "headline", "content", "approved_status", "independent_authors"]
