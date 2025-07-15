# tasks, urls.py:
from django.urls import path
from tasks import views


urlpatterns = [
    path('manager-dashboard/', views.ManagerDashboardView.as_view(), name="manager-dashboard"),
    path('employee-dashboard/', views.EmployeeDashboardView.as_view(), name="employee-dashboard"),    
    path('task-home/', views.TaskHomeView.as_view(), name='task-home'),
    path('view-tasks/', views.ViewTasksView.as_view(), name='view-tasks'),
	path('view_task/', views.ViewProject.as_view(), name='view-task'),  
	path('create-task/', views.CreateTask.as_view(), name='create-task'), # cbv
    path('update-task/<int:id>/', views.UpdateTaskView.as_view(), name='update-task'),
    path('delete-task/<int:id>/', views.DeleteTaskView.as_view(), name='delete-task'),
    path('task/<int:task_id>/details/', views.TaskDetail.as_view(), name='task-details'),    
	path('dashboard/', views.dashboard, name='dashboard')  # fbv
]