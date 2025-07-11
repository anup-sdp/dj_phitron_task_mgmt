# tasks, signals.py:
# https://docs.djangoproject.com/en/5.2/topics/signals/
# https://docs.djangoproject.com/en/5.2/ref/signals/

from django.db.models.signals import post_save, pre_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from tasks.models import Task
from django.contrib.auth import get_user_model
from django.conf import settings

@receiver(post_save, sender=Task)  # pre_save, pre_delete, post_delete etc
def notify_task_creation(sender, instance, created, **kwargs):
    if created:
        print("sender", sender)
        print("instance", instance) # task name
        print(kwargs)
        # instance.is_completed = True
        instance.save() # recursion if outside if, then created detached from kwargs, so now on created will be false.
        

@receiver(m2m_changed, sender=Task.assigned_to.through)
def notify_employees_on_task_creation(sender, instance, action, **kwargs):
    if action == 'post_add':
        print(instance, instance.assigned_to.all())

        assigned_emails = [emp.email for emp in instance.assigned_to.all()]
        print("Checking....", assigned_emails)

        send_mail(
            "New Task Assigned",
            f"You have been assigned to the task: {instance.title}",
            "task_mgmt_app",
            assigned_emails,
            fail_silently=False,
        )
        

"""
# not needed as on delete cascade
@receiver(post_delete, sender=Task)
def delete_associate_details(sender, instance, **kwargs):
    if instance.details:
        print(isinstance)
        instance.details.delete()

        print("Deleted successfully")
"""     


"""
send_mail("New Task Assigned",f"You have been assigned to the task: wow task","anup30coc@gmail.com","anupbarua30@gmail.com",fail_silently=False,) 
send_mail("New Task Assigned","You have been assigned to the task: wow task","anup30coc@gmail.com",["anupbarua30@gmail.com"],fail_silently=False)
send_mail(subject, message, settings.EMAIL_HOST_USER, [address])

"""   


"""
# remove notify_task_creation if use this.
@receiver(m2m_changed, sender=Task.assigned_to.through)
def notify_employees_on_task_change(sender, instance, action, pk_set, **kwargs):    
    # - On initial assignment (when task is first created and users are added),
    #   send "New Task Assigned" to all.
    # - On subsequent adds, send "Added to Task" only to newly added users.
    # - On removals, send "Removed from Task" only to users who were removed.
    
    # We're only interested in additions/removals, not clears or pre-hooks
    if action not in ('post_add', 'post_remove'):
        return

    #User = settings.AUTH_USER_MODEL
    User = get_user_model()
    # Find the actual User objects that were added/removed
    users = User.objects.filter(pk__in=pk_set)  # pk_set: just added/removed primary keys
    emails = [u.email for u in users if u.email]

    if not emails:
        return

    # INITIAL CREATION vs. LATER UPDATES:
    # At the moment of m2m post_add for a brand-new Task, created_at == updated_at.
    is_initial = (
        action == 'post_add' and instance.created_at and instance.updated_at and abs((instance.updated_at - instance.created_at).total_seconds()) < 1       
    )

    if action == 'post_add':
        if is_initial:
            subject = "New Task Assigned"
            body = f"You have been assigned a *new* task:\n\n  • {instance.title}\n\nPlease login to view the details."
                   
        else:
            subject = "Added to Task"
            body = f"You have been *added* to the existing task:\n\n  • {instance.title}\n\nPlease login to view the details."                   

    elif action == 'post_remove':
        subject = "Removed from Task"
        body = f"You have been *removed* from the task:\n\n  • {instance.title}\n\nIf this is unexpected, please contact your project manager."               

    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)
    except Exception as e:
        print("error:", e)
"""        


"""
# version 2, without relying on 1sec timing
_newly_created_tasks = set()

@receiver(post_save, sender=Task)
def track_new_task(sender, instance, created, **kwargs):
    #Track when a new task is created
    if created:
        _newly_created_tasks.add(instance.pk)

@receiver(m2m_changed, sender=Task.assigned_to.through)
def notify_employees_on_task_change(sender, instance, action, pk_set, **kwargs):
    
    # Handle task assignment notifications.    
    # This fires separately for each action:
    # - post_remove: for users being removed
    # - post_add: for users being added
    
    # Mixed operations (like task.assigned_to.set([new_users])) will trigger both.
    
    if action not in ('post_add', 'post_remove'):
        return
    
    if not pk_set:
        return
    
    User = get_user_model()
    users = User.objects.filter(pk__in=pk_set)
    emails = [u.email for u in users if u.email]
    
    if not emails:
        return
    
    # Determine email content based on action and context
    if action == 'post_add':
        # Check if this is the initial assignment for a new task
        is_initial = instance.pk in _newly_created_tasks
        
        if is_initial:
            # Remove from tracking set after initial assignment
            _newly_created_tasks.discard(instance.pk)
            subject = "New Task Assigned"
            body = f"You have been assigned a new task:\n\n  • {instance.title}\n\nPlease login to view the details."
        else:
            subject = "Added to Task"
            body = f"You have been added to the existing task:\n\n  • {instance.title}\n\nPlease login to view the details."
    
    elif action == 'post_remove':
        subject = "Removed from Task"
        body = f"You have been removed from the task:\n\n  • {instance.title}\n\nIf this is unexpected, please contact your project manager."
    
    # Send emails
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=False
        )
        print(f"Task notification sent to {len(emails)} users for task: {instance.title}")
    except Exception as e:
        print(f"Failed to send task notification: {e}")

# Optional: Clean up tracking set periodically to prevent memory leaks
@receiver(post_save, sender=Task)
def cleanup_tracking_set(sender, instance, created, **kwargs):
    #Clean up tracking set for tasks that might not get assigned to anyone
    if not created:
        # Remove from tracking if task is updated but still has no assignments
        if instance.pk in _newly_created_tasks and not instance.assigned_to.exists():
            _newly_created_tasks.discard(instance.pk)

""" 
