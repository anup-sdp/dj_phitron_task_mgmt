from django.urls import path
#from users.views import sign_up, sign_in, sign_out, activate_user, admin_dashboard, assign_role, create_group, group_list, CustomLoginView, ProfileView, ChangePassword, CustomPasswordResetView, CustomPasswordResetConfirmView, EditProfileView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

from users import views

"""
urlpatterns = [
    path('sign-up/', sign_up, name='sign-up'),
    # path('sign-in/', sign_in, name='sign-in'),  # http://127.0.0.1:8000/users/sign-in/
	path('sign-in/', LoginView.as_view(template_name="registration/login-1.html", next_page="home"), name='sign-in'),  # default: needs registration/login.html and accounts/profile/
	# ^ if next_page not given, will go to LOGIN_REDIRECT_URL in settings.
    #path('sign-in/', CustomLoginView.as_view(), name='sign-in'),
    #path('sign-out/', sign_out, name='logout'),
    path('sign-out/', LogoutView.as_view(), name='logout'),
    path('activate/<int:user_id>/<str:token>/', activate_user),  # email activation
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),  # http://127.0.0.1:8000/users/admin/dashboard
    path('admin/<int:user_id>/assign-role/', assign_role, name='assign-role'),
    path('admin/create-group/', create_group, name='create-group'),
    path('admin/group-list/', group_list, name='group-list'),
    path('profile/', ProfileView.as_view(), name='profile'),  # http://127.0.0.1:8000/users/profile/
    path('password-change/', ChangePassword.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),        
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),        
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),
]
"""

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