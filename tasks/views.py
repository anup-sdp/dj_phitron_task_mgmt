# tasks > views.py:
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Count, Max, Min, Avg, Q, Case, When, IntegerField

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from tasks.forms import TaskForm, TaskModelForm, TaskDetailModelForm
from django.contrib.auth import get_user_model
from .models import Task, Project



def is_employee(user):
    # add if superuser/admin ?
    return user.groups.filter(name='Employee').exists()

@user_passes_test(is_employee, login_url='no-permission')
def employee_dashboard(request):
    return render(request, "dashboard/employee-dashboard.html")


def is_manager(user):
    # add if superuser ?
    return user.groups.filter(name='Admin').exists() or user.groups.filter(name='Manager').exists()

@user_passes_test(is_manager, login_url='no-permission')
def manager_dashboard(request):    
    """
    # this approch makes more db queries
    tasks = Task.objects.all()
    total_task = tasks.count()
    completed_task = Task.objects.filter(status="COMPLETED").count()
    # completed_task = tasks.filter(status="COMPLETED").count()
    in_progress_task = Task.objects.filter(status='IN_PROGRESS').count()
    pending_task = Task.objects.filter(status="PENDING").count()
    counts = {
        "total_task": total_task,
        "completed_task": completed_task,
        "in_progress_task": in_progress_task,
        "pending_task": pending_task,
    }
    """
    """
    # optimized but verbose, good for more complex queries
    counts = Task.objects.aggregate(
        total_task=Count('id'),
        completed_task=Count(Case(When(status='COMPLETED', then=1), output_field=IntegerField())),
        in_progress_task=Count(Case(When(status='IN_PROGRESS', then=1), output_field=IntegerField())),
        pending_task=Count(Case(When(status='PENDING', then=1), output_field=IntegerField())),)
    """
    # optimized db query
    counts = Task.objects.aggregate(
        total_task=Count("id"),
        completed_task=Count("id", filter=Q(status="COMPLETED")),
        in_progress_task=Count("id", filter=Q(status="IN_PROGRESS")),
        pending_task=Count("id", filter=Q(status="PENDING")),
    )
    type = request.GET.get('type', 'all')
    qs = Task.objects.select_related('details').prefetch_related('assigned_to')  # select_related (for OneToOneField/ForeignKey) vs prefetch_related (ManyToManyField/reverse relations)    
    if type == 'completed':
        tasks = qs.filter(status='COMPLETED')
    elif type == 'in_progress':
        tasks = qs.filter(status='IN_PROGRESS')
    elif type == 'pending':
        tasks = qs.filter(status='PENDING')
    elif type == 'all':
        tasks = qs.all()
    
    context = {
        "tasks": tasks,
        "counts": counts
    }
    return render(request, "dashboard/manager-dashboard.html", context)

def test(request):
    names = ["Mary Jane", "John Paul", "emma grace", "anna", "mr x"]
    context = {
        "names": names,
        "age": 23,
        "count": len(names)
    }
    return render(request, 'test.html', context)

def task_home(request):
    return render(request, "task-home.html")



"""
# using TaskForm
def create_task(request):
    User = get_user_model()
    employees = User.objects.all()
    if request.method == "POST":
        form = TaskForm(request.POST, employees=employees)
        if form.is_valid():
            #print(form.cleaned_data)
            data = form.cleaned_data
            title = data.get('title')
            description = data.get('description')
            due_date = data.get('due_date')            
            assigned_ids = data['assigned_to']  # list of user IDs
            users_qs = User.objects.filter(id__in=assigned_ids)
            task = Task.objects.create(title=title, description=description, due_date=due_date)
            task.assigned_to.set(users_qs)
            messages.success(request, "Task Created Successfully")
            return redirect('create-task')
            
    form = TaskForm(employees=employees)    
    context = {"task_form":form}
    return render(request, "task_form.html", context)
"""


""""""
# using TaskModelForm
@login_required
@permission_required("tasks.add_task", login_url='no-permission')
def create_task(request):
    if request.method == "POST":
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():           
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Created Successfully")
            #return redirect('create-task')  # message not showing after creating task. get method message is showing. for redirect to same page
            return redirect('task-home') # now showing the success message
        
    task_form = TaskModelForm()
    task_detail_form = TaskDetailModelForm()
    context = {"task_form": task_form, "task_detail_form": task_detail_form, "messages": {"create_task called in get method",}}
    return render(request, "task_form.html", context)


# variable for list of decorators
create_decorators = [login_required, permission_required(
    "tasks.add_task", login_url='no-permission')]

@login_required
@permission_required("tasks.view_task", login_url='no-permission')
def view_tasks(request):
    # tasks = Task.objects.all()
    tasks = Task.objects.prefetch_related('assigned_to').all()
    task_count = Task.objects.aggregate(total=Count('id')) # get by task_count.total  # aggregate functions
    projects = Project.objects.annotate(num_tasks= Count('task')).order_by('name').prefetch_related('task').all() # annotate: create new field, prefetch_related: avoids 1+n query    
    
    return render(request, "show_task.html", {"tasks": tasks, "projects": projects})

from django.shortcuts import get_object_or_404

@login_required
@permission_required("tasks.change_task", login_url='no-permission')
def update_task(request, id):
    #task = Task.objects.get(id=id)
    task = get_object_or_404(Task, id=id)
        
    if hasattr(task, 'details'):  # handle error: task dont have details
        detail = task.details
    else:
        detail = None
    if request.method == "POST":
        task_form = TaskModelForm(request.POST, instance=task)
        task_detail_form = TaskDetailModelForm(request.POST, instance=detail)
        if task_form.is_valid() and task_detail_form.is_valid():
            # For Model Form Data 
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, f"Task: {task.title}, Updated Successfully")
            # return redirect('update-task', id=task.id)
            return redirect('manager-dashboard')

    task_form = TaskModelForm(instance=task)  # For GET
    task_detail_form = TaskDetailModelForm(instance=detail)    
    context = {"task_form": task_form, "task_detail_form": task_detail_form}
    return render(request, "task_form.html", context)

@login_required
@permission_required("tasks.delete_task", login_url='no-permission')
def delete_task(request, id):
    if request.method == 'POST':
        task = Task.objects.get(id=id)
        task.delete()
        messages.success(request, 'Task Deleted Successfully')
        return redirect('manager-dashboard')
    else:
        messages.error(request, 'Something went wrong')
        return redirect('manager-dashboard')


@login_required
@permission_required("tasks.view_task", login_url='no-permission')
def task_details(request, task_id):
    task = Task.objects.get(id=task_id)
    status_choices = Task.STATUS_CHOICES

    if request.method == 'POST':
        selected_status = request.POST.get('task_status')
        print(selected_status)
        task.status = selected_status
        task.save()
        return redirect('task-details', task.id)

    return render(request, 'task_details.html', {"task": task, 'status_choices': status_choices})

from users.views import is_admin

@login_required
def dashboard(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('employee-dashboard')    

    return redirect('no-permission')