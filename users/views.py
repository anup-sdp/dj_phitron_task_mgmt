from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm, EditProfileForm
from django.contrib import messages
from users.forms import LoginForm  # LoginForm (customized) vs AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
#
from django.views.generic import TemplateView, UpdateView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


User = get_user_model()


def is_admin(user):
    # add if superuser ?
    return user.groups.filter(name='Admin').exists()


class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect('profile')


class SignUpView(FormView):
    form_class = CustomRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get('password1'))
        user.is_active = False  # was False, to activate using email.
        user.save()
        messages.success(self.request, 'A Confirmation mail sent. Please check your email')
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is not valid:", form.errors)
        return super().form_invalid(form)

    
class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login-1.html'

    def get_success_url(self):
        next_url = self.request.GET.get('next')  # eg. non logged in http://127.0.0.1:8000/tasks/create-task/ to http://127.0.0.1:8000/users/sign-in/?next=/tasks/create-task/
        return next_url if next_url else super().get_success_url()

    def form_invalid(self, form):
        messages.error(self.request, 'No activated user found with these credentials.')
        return super().form_invalid(form)	
  

class SignOutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        return redirect('sign-in')	


 # cbv not needed for this
def activate_user(request, user_id, token): 
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, f"User account of: { user.username}, has been activated")   
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid Id or token')

    except User.DoesNotExist:
        return HttpResponse('User not found')



class AdminDashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'admin/admin_dashboard.html'
    login_url = 'no-permission'

    def test_func(self):
        return is_admin(self.request.user)   # calls the is_admin function

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.prefetch_related(
            Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
        ).all()
        
        for user in users:
            if user.all_groups:
                user.group_name = user.all_groups[0].name
            else:
                user.group_name = 'No Group Assigned'
        
        context['users'] = users
        return context


class AssignRoleView(UserPassesTestMixin, FormView):
    form_class = AssignRoleForm
    template_name = 'admin/assign_role.html'
    success_url = reverse_lazy('admin-dashboard')
    login_url = 'sign-in'

    def test_func(self):
        return is_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(id=self.kwargs['user_id'])
        context['username'] = user.username
        return context

    def form_valid(self, form):
        user = User.objects.get(id=self.kwargs['user_id'])
        role = form.cleaned_data.get('role')
        user.groups.clear()  # Remove old roles
        user.groups.add(role)
        messages.success(self.request, f'User "{user.username}" has been assigned to the "{role.name}" role')
        return super().form_valid(form)
    


class CreateGroupView(UserPassesTestMixin, FormView):
    form_class = CreateGroupForm
    template_name = 'admin/create_group.html'
    success_url = reverse_lazy('create-group')
    login_url = 'no-permission'

    def test_func(self):
        return is_admin(self.request.user)

    def form_valid(self, form):
        group = form.save()
        messages.success(self.request, f'Group {group.name} has been created successfully')
        return super().form_valid(form)



class GroupListView(UserPassesTestMixin, TemplateView):
    template_name = 'admin/group_list.html'
    login_url = 'no-permission'

    def test_func(self):
        return is_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.prefetch_related('permissions').all()
        return context


class ProfileView(TemplateView):  # https://docs.djangoproject.com/en/5.2/ref/class-based-views/base/
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()  # builtin
        context['bio'] = user.bio
        context['profile_image'] = user.profile_image

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context


class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm
    

# password reset tested, ok.
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'A Reset email sent. Please check your email')            
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset success!')
        return super().form_valid(form)

    
# Role Based Access Control (RBAC)
