# video 7.3, Faker: is a Python package that generates fake data  
# https://faker.readthedocs.io/en/master/ # pip install Faker
# alternatives: admin panel entry, manage.py shell, django fixtures, django-seed library for random data, 

import os
import django
from faker import Faker
import random
from tasks.models import Project, Task, TaskDetail
from users.models import CustomUser
# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_management.settings')
django.setup()

# Function to populate the database


def populate_db():
    # Initialize Faker
    fake = Faker()

    # Create Projects
    projects = [Project.objects.create(
        name=fake.bs().capitalize(),
        description=fake.paragraph(),
        start_date=fake.date_this_year()
    ) for _ in range(5)]
    print(f"Created {len(projects)} projects.")
	# Create employees
    employees = [CustomUser.objects.create(username=fake.name(), email=fake.email()) for _ in range(3)] # error
    print(f"Created {len(employees)} employees.")

    # Create Tasks
    tasks = []
    for _ in range(20):
        task = Task.objects.create(
            project=random.choice(projects),
            title=fake.sentence(),
            description=fake.paragraph(),
            due_date=fake.date_this_year(),
            status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED']),
            is_completed=random.choice([True, False])
        )
        task.assigned_to.set(random.sample(employees, random.randint(1, 3)))
        tasks.append(task)
    print(f"Created {len(tasks)} tasks.")

    # Create Task Details
    for task in tasks:
        TaskDetail.objects.create(
            task=task,
            assigned_to=", ".join(
                [emp.name for emp in task.assigned_to.all()]),
            priority=random.choice([ 'L', 'M', 'H']),
            notes=fake.paragraph()
        )
    print("Populated TaskDetails for all tasks.")
    print("Database populated successfully!")


def create_users():
    fake = Faker()
    users_created = []
    for _ in range(3):        
        username = fake.unique.user_name()              
        user = CustomUser.objects.create_user(
            username=username, 
            email=f"{username}@example.com", 
            password="1234"
        )
        users_created.append(user)
    print(f"Successfully created {len(users_created)} users.")    
    

"""
in cmd run:
python manage.py shell
>>> from populate_db import create_users
>>> create_users()

import os
os.system('cls' if os.name == 'nt' else 'clear')
"""
