# tasks, urls.py:
from django.urls import path
from tasks.views import manager_dashboard, employee_dashboard, test, create_task, task_home, view_tasks, update_task, delete_task, task_details, dashboard, ViewProject

urlpatterns = [
    path('manager-dashboard/', manager_dashboard, name="manager-dashboard"),  # http://127.0.0.1:8000/tasks/manager-dashboard/   (ok- add margin)
    path('employee-dashboard/', employee_dashboard,  name="employee-dashboard"),   # http://127.0.0.1:8000/tasks/employee-dashboard/   (ok- add margin)
    path('test/', test),
	path('task-home/', task_home, name='task-home'),
	path('view-tasks/', view_tasks, name='view-tasks'),  # http://127.0.0.1:8000/tasks/view-tasks/
	# path('view_task/', ViewProject.as_view(), name='view-task'),
	path('create-task/', create_task, name='create-task'), # fbv # http://127.0.0.1:8000/tasks/create-task/
	path('update-task/<int:id>/', update_task, name='update-task'),
	path('delete-task/<int:id>/', delete_task, name='delete-task'),
	path('task/<int:task_id>/details/', task_details, name='task-details'), # ok
	path('dashboard', dashboard, name='dashboard')
    #path('create-task/', CreateTask.as_view(), name='create-task'), # cbv
]
