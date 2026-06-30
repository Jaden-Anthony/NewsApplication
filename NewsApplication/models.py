from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

# Content Models


class Article(models.Model):

    headline = models.CharField(max_length=100)
    content = models.TextField(max_length=2500)
    approved_status = models.BooleanField(default=False)

    def __str__(self):
        return self.headline


class Newsletter(models.Model):

    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title


# publisher Model


class Publisher(models.Model):

    name = models.CharField(max_length=30)
    # Defines the relationship allowing multiple editors and journalists per publisher
    editors = models.ManyToManyField(
        "CustomUser", related_name="publisher_editors", blank=True
    )
    journalists = models.ManyToManyField(
        "CustomUser", related_name="publisher_journalists", blank=True
    )

    def __str__(self):
        return self.name


# CustomUser Model


class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ("reader", "Reader"),
        ("editor", "Editor"),
        ("journalist", "Journalist"),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default="reader")

    # --- Reader Specific Fields ---
    publisher_subscriptions = models.ManyToManyField(
        Publisher, blank=True, related_name="subscribers"
    )
    journalist_subscriptions = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="followers"
    )

    # --- Journalist Specific Fields ---
    independent_articles = models.ManyToManyField(
        Article, blank=True, related_name="independent_authors"
    )
    independent_newsletters = models.ManyToManyField(
        Newsletter, blank=True, related_name="independent_authors"
    )

    def save(self, *args, **kwargs):
        # Save the instance first so ManyToMany fields have a primary key to reference
        super().save(*args, **kwargs)

        # Enforce mutually exclusive fields by clearing the opposing role's data
        if self.role == "journalist":
            self.publisher_subscriptions.clear()
            self.journalist_subscriptions.clear()
        elif self.role == "reader":
            self.independent_articles.clear()
            self.independent_newsletters.clear()


# Automation: Roles, Groups, and Permissions Signal
@receiver(post_save, sender=CustomUser)
def manage_user_roles_and_permissions(sender, instance, created, **kwargs):
    if instance.role:
        # Retrieve or create the group matching the user's role
        group_name = instance.role.capitalize()
        group, group_created = Group.objects.get_or_create(name=group_name)

        # If the group was just created, build its permission matrix
        if group_created:
            article_ct = ContentType.objects.get_for_model(Article)
            newsletter_ct = ContentType.objects.get_for_model(Newsletter)

            # Fetch default Django permissions for the models
            view_art = Permission.objects.get(
                codename="view_article", content_type=article_ct
            )
            add_art = Permission.objects.get(
                codename="add_article", content_type=article_ct
            )
            change_art = Permission.objects.get(
                codename="change_article", content_type=article_ct
            )
            del_art = Permission.objects.get(
                codename="delete_article", content_type=article_ct
            )

            view_news = Permission.objects.get(
                codename="view_newsletter", content_type=newsletter_ct
            )
            add_news = Permission.objects.get(
                codename="add_newsletter", content_type=newsletter_ct
            )
            change_news = Permission.objects.get(
                codename="change_newsletter", content_type=newsletter_ct
            )
            del_news = Permission.objects.get(
                codename="delete_newsletter", content_type=newsletter_ct
            )

            # Assign permissions based on requirements
            if group_name == "Reader":
                group.permissions.add(view_art, view_news)

            elif group_name == "Editor":
                # Note: Instructions state Editor can view, update, delete (no 'create' explicitly mentioned)
                group.permissions.add(view_art, change_art, del_art)
                group.permissions.add(view_news, change_news, del_news)

            elif group_name == "Journalist":
                group.permissions.add(view_art, add_art, change_art, del_art)
                group.permissions.add(view_news, add_news, change_news, del_news)

        # Clear existing groups and assign the correct one
        instance.groups.clear()
        instance.groups.add(group)


@receiver(post_save, sender=CustomUser)
def enforce_role_field_nullification(sender, instance, created, **kwargs):
    """
    Ensures that if a user is a Journalist, their Reader fields are strictly empty ('None'),
    and if they are a Reader, their Journalist fields are strictly empty.
    """
    # M2M fields can only be cleared if the user object has already been saved to the DB
    if instance.pk:
        if instance.role == "journalist":
            instance.publisher_subscriptions.clear()
            instance.journalist_subscriptions.clear()

        elif instance.role == "reader":
            instance.independent_articles.clear()
            instance.independent_newsletters.clear()

        elif instance.role == "editor":
            # Editors manage the system, they shouldn't have reader/journalist specific data
            instance.publisher_subscriptions.clear()
            instance.journalist_subscriptions.clear()
            instance.independent_articles.clear()
            instance.independent_newsletters.clear()
