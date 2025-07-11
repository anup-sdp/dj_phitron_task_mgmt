# tasks > models.py
from django.db import models
from django.conf import settings


# models.OneToOneField
# models.ForeignKey : for Many-to-One field
# models.ManyToManyField

class Task(models.Model):
    # iterables of 2 valued tuples
    STATUS_CHOICES = [('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')]
    # ^ see preferred way in drf lms project, ostad.
    project = models.ForeignKey("Project", on_delete=models.CASCADE, null=True, blank=True, related_name="task")  
    # quotation marks to handle a forward reference, lazy relationship. as Project class is written latter.
    # ^ related_name ?
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")
    # assigned_to = models.ManyToManyField(Employee, related_name='tasks')
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='tasks')  # tasks_task_assigned_to table gets created in db. 
    title = models.CharField(max_length=250)
    description = models.TextField()
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # details

    def __str__(self):
        return self.title


class TaskDetail(models.Model):    
    LOW = 'L'  # saved in database as 'L' , detail.get_priority_display() : 'Low'
    MEDIUM = 'M'
    HIGH = 'H'
    PRIORITY_OPTIONS = ((LOW, 'Low'), (MEDIUM, 'Medium'), (HIGH, 'High'))
    priority = models.CharField(max_length=1, choices=PRIORITY_OPTIONS, default=LOW)
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='details')  # foreign key, OneToOneField # related_name for reverse relationship
    asset = models.ImageField(upload_to='tasks_asset', blank=True, null=True, default="tasks_asset/default_img.png")
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Details of Task: {self.task.title}"


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()

    def __str__(self):
        return self.name
    

# https://docs.djangoproject.com/en/5.2/topics/db/models/
# django model fields: https://docs.djangoproject.com/en/5.2/ref/models/fields/


"""
# signals
from django.db.models.signals import post_save, pre_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail

@receiver(post_save, sender=Task)  # pre_save, pre_delete, post_delete etc
def notify_task_creation(sender, instance, created, **kwargs):
    if created:
        print("sender", sender)
        print("instance", instance) # task name
        print(kwargs)
        # instance.is_completed = True
        instance.save() # recursion if outside if, then created detached from kwargs, so now on created will be false.


@receiver(post_save, sender=Task) # post_saved not worked for this ?
def notify_employees_on_task_creation(sender, instance, created, **kwargs):
    if created:
        #print(instance, instance.assigned_to.all())
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