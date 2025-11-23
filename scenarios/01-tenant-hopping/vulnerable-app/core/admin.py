from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Tenant, Patient


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Add tenant to the user edit form
    fieldsets = BaseUserAdmin.fieldsets + (("Tenant Info", {"fields": ("tenant",)}),)

    # VULNERABILITY: Incomplete Visibility Filter
    # We filter the list so Bob only sees Bob.
    # But we don't validate if Bob is *allowed* to set the tenant field in POST requests.
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # The "Blinders": Only show users in my tenant
        return qs.filter(tenant=request.user.tenant)


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
