from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

from users import views


urlpatterns = [
    path('sign-up/', views.SignUpView.as_view(), name='sign-up'),
    path('sign-in/', views.CustomLoginView.as_view(), name='sign-in'),    
    path('sign-out/', LogoutView.as_view(), name='logout'),
    path('activate/<int:user_id>/<str:token>/', views.activate_user), # fbv    
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/<int:user_id>/assign-role/', views.AssignRoleView.as_view(), name='assign-role'),
    path('admin/create-group/', views.CreateGroupView.as_view(), name='create-group'),
    path('admin/group-list/', views.GroupListView.as_view(), name='group-list'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password-change/', views.ChangePassword.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit_profile')
]