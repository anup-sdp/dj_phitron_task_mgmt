# tasks > views.py:
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Count, Max, Min, Avg, Q, Case, When, IntegerField

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from tasks.forms import TaskForm, TaskModelForm, TaskDetailModelForm
from django.contrib.auth import get_user_model
from .models import Task, Project
from django.shortcuts import get_object_or_404
# for cbv:
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, TemplateView
from django.utils.decorators import method_decorator

def is_employee(user):
    # add if superuser/admin ?
    return user.groups.filter(name='Employee').exists()


def is_manager(user):
    # add if superuser ?
    return user.groups.filter(name='Admin').exists() or user.groups.filter(name='Manager').exists()

"""
@user_passes_test(is_employee, login_url='no-permission')
def employee_dashboard(request):
    return render(request, "dashboard/employee-dashboard.html")
"""

class EmployeeDashboardView(UserPassesTestMixin, TemplateView):
    template_name = "dashboard/employee-dashboard.html"
    login_url = 'no-permission'
    
    def test_func(self):
        return is_employee(self.request.user)

"""
@user_passes_test(is_manager, login_url='no-permission')
def manager_dashboard(request):    
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
"""
class ManagerDashboardView(UserPassesTestMixin, TemplateView):
    template_name = "dashboard/manager-dashboard.html"
    login_url = 'no-permission'
    
    def test_func(self):
        return is_manager(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Optimized db query
        counts = Task.objects.aggregate(
            total_task=Count("id"),
            completed_task=Count("id", filter=Q(status="COMPLETED")),
            in_progress_task=Count("id", filter=Q(status="IN_PROGRESS")),
            pending_task=Count("id", filter=Q(status="PENDING")),
        )
        
        type_filter = self.request.GET.get('type', 'all')
        qs = Task.objects.select_related('details').prefetch_related('assigned_to')
        
        if type_filter == 'completed':
            tasks = qs.filter(status='COMPLETED')
        elif type_filter == 'in_progress':
            tasks = qs.filter(status='IN_PROGRESS')
        elif type_filter == 'pending':
            tasks = qs.filter(status='PENDING')
        else:
            tasks = qs.all()
        
        context.update({
            "tasks": tasks,
            "counts": counts
        })
        return context

"""
def task_home(request):
    return render(request, "task-home.html")
"""

class TaskHomeView(TemplateView):
    template_name = "task-home.html"


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


"""
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
"""



# video 15.3: code at https://github.com/phitronio/SDT-Django/blob/module-15/task-management/tasks/views.py
# https://docs.djangoproject.com/en/5.2/topics/class-based-views/
# https://docs.djangoproject.com/en/5.2/topics/auth/default/
# use @method_decorator or auth mixins: LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import ContextMixin
from django.views import View

# cbv
class CreateTask(ContextMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
	# MRO: Method Resolution Order: the order in which Python walks through the base classes to find the method/attribute you asked for.
    # For creating task
    permission_required = 'tasks.add_task'
    login_url = 'sign-in'
    template_name = 'task_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = kwargs.get('task_form', TaskModelForm())
        context['task_detail_form'] = kwargs.get(
            'task_detail_form', TaskDetailModelForm())
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, "Task Created Successfully")
            return redirect('view-tasks')   # or wherever you want
        else:
            # Only here you need the context to redisplay the form with errors
            messages.error(request, "form is invalid")
            context = self.get_context_data(
                task_form=task_form,
                task_detail_form=task_detail_form
            )
            return render(request, self.template_name, context)


"""
@login_required
@permission_required("tasks.view_task", login_url='no-permission')
def view_tasks(request):  # task list, should be view_projects ?
    # tasks = Task.objects.all()
    tasks = Task.objects.prefetch_related('assigned_to').all()
    task_count = Task.objects.aggregate(total=Count('id')) # get by task_count.total  # aggregate functions
    projects = Project.objects.annotate(num_tasks= Count('task')).order_by('name').prefetch_related('task').all() # annotate: create new field, prefetch_related: avoids 1+n query    
    
    return render(request, "show_task.html", {"tasks": tasks, "projects": projects})
"""

class ViewTasksView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "tasks.view_task"
    login_url = 'no-permission'
    template_name = "show_task.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = Task.objects.prefetch_related('assigned_to').all()
        task_count = Task.objects.aggregate(total=Count('id'))
        projects = Project.objects.annotate(num_tasks=Count('task')).order_by('name').prefetch_related('task').all()
        
        context.update({
            "tasks": tasks,
            "projects": projects
        })
        return context




view_project_decorators = [login_required, permission_required("projects.view_project", login_url='no-permission')]

# cbv
@method_decorator(view_project_decorators, name='dispatch')
class ViewProject(ListView):
    model = Project
    context_object_name = 'projects'
    template_name = 'show_task.html'

    def get_queryset(self):
        queryset = Project.objects.annotate(num_task=Count('task')).order_by('num_task')
        return queryset
   


@login_required
@permission_required("tasks.view_task", login_url='no-permission')
def task_details(request, task_id):  # details of one task
    task = Task.objects.get(id=task_id)
    status_choices = Task.STATUS_CHOICES

    if request.method == 'POST':
        selected_status = request.POST.get('task_status')
        print(selected_status)
        task.status = selected_status
        task.save()
        return redirect('task-details', task.id)

    return render(request, 'task_details.html', {"task": task, 'status_choices': status_choices})


class TaskDetail(DetailView):
    model = Task
    template_name = 'task_details.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # {"task": task}
        # {"task": task, 'status_choices': status_choices}
        context['status_choices'] = Task.STATUS_CHOICES
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        selected_status = request.POST.get('task_status')
        task.status = selected_status
        task.save()
        return redirect('task-details', task.id)



"""
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

    task_form = TaskModelForm(instance=task)  # For GET, status update ? ------------ separate update form ?
    task_detail_form = TaskDetailModelForm(instance=detail)
    context = {"task_form": task_form, "task_detail_form": task_detail_form}
    return render(request, "task_form.html", context)


class UpdateTask(UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = self.get_form()
        print(context)
        if hasattr(self.object, 'details') and self.object.details:
            context['task_detail_form'] = TaskDetailModelForm(instance=self.object.details)                
        else:
            context['task_detail_form'] = TaskDetailModelForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance=self.object)

        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=getattr(self.object, 'details', None))

        if task_form.is_valid() and task_detail_form.is_valid():

            # For Model Form Data
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Updated Successfully")
            return redirect('update-task', self.object.id)
        return redirect('update-task', self.object.id)
"""    

class UpdateTaskView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'
    permission_required = "tasks.change_task"
    login_url = 'no-permission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = self.get_form()
        
        if hasattr(self.object, 'details') and self.object.details:
            context['task_detail_form'] = TaskDetailModelForm(instance=self.object.details)
        else:
            context['task_detail_form'] = TaskDetailModelForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance=self.object)
        
        detail_instance = getattr(self.object, 'details', None)
        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=detail_instance)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, f"Task: {task.title}, Updated Successfully")
            return redirect('manager-dashboard')
        else:
            context = self.get_context_data(
                task_form=task_form,
                task_detail_form=task_detail_form
            )
            return render(request, self.template_name, context)
    

"""
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
"""
class DeleteTaskView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "tasks.delete_task"
    login_url = 'no-permission'
    
    def post(self, request, *args, **kwargs):
        task_id = kwargs.get('id')
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        messages.success(request, 'Task Deleted Successfully')
        return redirect('manager-dashboard')
    
    def get(self, request, *args, **kwargs):
        messages.error(request, 'Something went wrong')
        return redirect('manager-dashboard')



class TaskDetail(DetailView):
    model = Task
    template_name = 'task_details.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # {"task": task}
        # {"task": task, 'status_choices': status_choices}
        context['status_choices'] = Task.STATUS_CHOICES
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        selected_status = request.POST.get('task_status')
        task.status = selected_status
        task.save()
        return redirect('task-details', task.id)

from users.views import is_admin
# cbv not needed for dashboard
@login_required
def dashboard(request):  
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('employee-dashboard')

    return redirect('no-permission')