from django.db import models
from django.contrib.auth.models import AbstractUser


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    # The 'Keys to the Kingdom'
    # If this field is changed, the user moves to a different tenant
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, null=True, blank=True, related_name="users"
    )


class Profile(User):
    """
    Proxy Model for User.
    This is the "Security by Obscurity" trick.
    We rename 'Users' to 'My Profile' in the admin UI to make it look harmless.
    But under the hood, it's still the User model with the vulnerable tenant field.
    """

    class Meta:
        proxy = True
        verbose_name = "My Profile"
        verbose_name_plural = "My Profile"
        # Ensure Django creates permissions for this proxy model
        default_permissions = ("add", "change", "delete", "view")


class Patient(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="patients"
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    diagnosis = models.TextField()
    # Sensitive medical data - In a real app, this would be encrypted

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.diagnosis})"
