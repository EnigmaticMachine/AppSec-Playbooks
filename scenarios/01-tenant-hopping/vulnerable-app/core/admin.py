from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Tenant, Patient


# SECURITY BY OBSCURITY: Hide the "Users" model from the admin
# We unregister it so non-superusers don't see it in the sidebar
# Instead, we show "My Profile" which is a proxy to User
@admin.register(Profile)
class ProfileAdmin(BaseUserAdmin):
    """
    This is the "disguised" User admin.
    It looks like a harmless "My Profile" page, but it's actually the full User model.
    The vulnerability: We filter the list view, but we don't validate POST data.
    """

    # Add tenant to the user edit form
    fieldsets = BaseUserAdmin.fieldsets + (("Tenant Info", {"fields": ("tenant",)}),)

    # VULNERABILITY: Incomplete Visibility Filter
    # We filter the list so Bob only sees Bob.
    # But we don't validate if Bob is *allowed* to set the tenant field in POST requests.
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # The "Blinders": Only show the logged-in user
        # This makes it look like a "My Profile" page
        return qs.filter(id=request.user.id)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "diagnosis", "tenant")

    # Same logic: Only show patients in my tenant
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if not request.user.tenant:
            return qs.none()
        return qs.filter(tenant=request.user.tenant)


# Register Tenant so Superuser can manage them
admin.site.register(Tenant)
