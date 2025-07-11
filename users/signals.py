# users, signals.py:
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
# from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail

OurUser = get_user_model()

@receiver(post_save, sender=OurUser)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}/"
        subject = 'Activate Your Account'
        message = (
            f'Hi {instance.username},\n\n'
            f'Activate your account by clicking the link below:\n'
            f'{activation_url}\n\nThank You!'
        )
        recipient_list = [instance.email]
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)                      
        except Exception as e:
            print(f"Failed to send email to {instance.email}: {str(e)}")
            

@receiver(post_save, sender=OurUser)
def assign_role(sender, instance, created, **kwargs):
    if created:
        user_group, created = Group.objects.get_or_create(name='User')  # returns tuple
        instance.groups.add(user_group)
        #instance.save()  # no need to call, here—the m2m add() is enough
        # Avoid calling save() inside a post_save