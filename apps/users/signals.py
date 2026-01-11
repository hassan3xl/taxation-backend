# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import TaxPayer

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_taxpayer_profile(sender, instance, created, **kwargs):
    if created:
        # Create an empty TaxPayer profile for every new user
        TaxPayer.objects.create(
            user=instance,
            full_name=instance.first_name + " " + instance.last_name, # or generic
        )