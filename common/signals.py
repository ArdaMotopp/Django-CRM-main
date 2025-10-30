# common/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from common.models import Profile, Org

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile (with Org) for new users"""
    if created:
        # Ensure a default org exists
        org, _ = Org.objects.get_or_create(name="Default Org")
        # Ensure a profile is created for this user
        Profile.objects.get_or_create(user=instance, defaults={"org": org})
