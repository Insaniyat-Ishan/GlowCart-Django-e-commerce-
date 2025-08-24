from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Address

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Address)
def ensure_single_default(sender, instance, **kwargs):
    if instance.is_default:
        Address.objects.filter(user=instance.user).exclude(id=instance.id).update(is_default=False)
