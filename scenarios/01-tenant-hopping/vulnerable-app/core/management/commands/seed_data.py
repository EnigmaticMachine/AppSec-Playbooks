from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Tenant, Patient, Profile

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with MediVault scenario data"

    def handle(self, *args, **options):
        self.stdout.write("Cleaning old data...")
        Patient.objects.all().delete()
        User.objects.all().delete()
        Tenant.objects.all().delete()
        Group.objects.all().delete()

        self.stdout.write("Creating Tenants...")
        clinic_a = Tenant.objects.create(name="Downtown Clinic (Victim)")  # ID 1
        clinic_b = Tenant.objects.create(name="Uptown Urgent Care (Attacker)")  # ID 2

        self.stdout.write("Creating Users...")
        # 1. Superuser
        User.objects.create_superuser("admin", "admin@medivault.com", "admin")

        # 2. Dr. Alice (The Victim) - ID 1
        alice = User.objects.create_user("alice", "alice@downtown.com", "password123")
        alice.first_name = "Alice"
        alice.last_name = "Wonder"
        alice.tenant = clinic_a
        alice.is_staff = True  # Needs admin access
        alice.save()

        # 3. Dr. Bob (The Attacker) - ID 2
        bob = User.objects.create_user("bob", "bob@uptown.com", "password123")
        bob.first_name = "Bob"
        bob.last_name = "Builder"
        bob.tenant = clinic_b
        bob.is_staff = True  # Needs admin access
        bob.save()

        self.stdout.write("Creating Doctors group...")
        # Create the Doctors group
        doctors_group = Group.objects.create(name="Doctors")

        # Get content types for Profile and Patient models
        # For proxy models, we need for_concrete_model=False to get a separate ContentType
        profile_content_type = ContentType.objects.get_for_model(
            Profile, for_concrete_model=False
        )
        patient_content_type = ContentType.objects.get_for_model(Patient)

        # Create permissions for Profile if they don't exist
        # Django doesn't auto-create permissions for proxy models, so we do it manually
        view_profile_perm, _ = Permission.objects.get_or_create(
            codename="view_profile",
            content_type=profile_content_type,
            defaults={"name": "Can view My Profile"},
        )
        change_profile_perm, _ = Permission.objects.get_or_create(
            codename="change_profile",
            content_type=profile_content_type,
            defaults={"name": "Can change My Profile"},
        )

        # Get the view_patient permission
        view_patient_perm = Permission.objects.get(
            codename="view_patient", content_type=patient_content_type
        )

        # Add permissions to the Doctors group
        doctors_group.permissions.add(
            view_profile_perm, change_profile_perm, view_patient_perm
        )

        # Add Alice and Bob to the Doctors group
        alice.groups.add(doctors_group)
        bob.groups.add(doctors_group)

        self.stdout.write("Creating Patients...")
        # Alice's Patients (The Secret Data)
        Patient.objects.create(
            tenant=clinic_a,
            first_name="John",
            last_name="Doe",
            diagnosis="HIV Positive - Confidential",
        )
        Patient.objects.create(
            tenant=clinic_a,
            first_name="Sarah",
            last_name="Connor",
            diagnosis="Terminator Trauma",
        )

        # Bob's Patients
        Patient.objects.create(
            tenant=clinic_b,
            first_name="Mike",
            last_name="Wazowski",
            diagnosis="Eye Infection",
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded MediVault!"))
        self.stdout.write(f"Tenant 1 ID: {clinic_a.id}")
        self.stdout.write(f"Tenant 2 ID: {clinic_b.id}")
