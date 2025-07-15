# fixed code: user add in admin panel.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

CustomUser = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    readonly_fields = ('last_login', 'date_joined', 'profile_image_tag', 'profile_image_display')  #
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'profile_image_tag')    
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_image', 'profile_image_display')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'bio', 'profile_image'),
        }),
    )
    
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-username',)
    
    # helper to render the thumbnail 
    def profile_image_display(self, obj):
        if obj.profile_image and obj.profile_image.url:
            return format_html(
                '<img src="{}" style="max-height: 100px; border-radius:50%;" />',
                obj.profile_image.url
            )
        return "(no image)"
    profile_image_display.short_description = "Profile Image display"
    
    def profile_image_tag(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="50" style="object-fit: cover;" />',
                obj.profile_image.url
            )
        return '—'
    profile_image_tag.short_description = 'Preview'
