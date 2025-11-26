from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# ===== Custom User Manager =====
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, user_type='adopter', **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, user_type='admin', **extra_fields)


# ===== Custom User =====
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('adopter', 'Adopter'),
        ('owner', 'Owner'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    name = models.CharField(max_length=150, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    is_approved = models.BooleanField(default=False)  # Only matters for owner

    objects = CustomUserManager()

    def __str__(self):
        return self.username

# ===== Pet Model =====
class Pet(models.Model):
    SIZE_CHOICES = (("Small","Small"),("Medium","Medium"),("Large","Large"))
    GENDER_CHOICES = (("Male","Male"),("Female","Female"))

    name = models.CharField(max_length=100)
    age = models.CharField(max_length=50)
    breed = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    description = models.TextField()
    image = models.ImageField(upload_to='pet_images/')
    location = models.CharField(max_length=200)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='pets')
    contact = models.CharField(max_length=100, blank=True, null=True)  # <-- NEW
    is_adopted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"
# ===================== SHELTER BOOKING =====================
from django.conf import settings

class ShelterBooking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shelter_bookings"
    )
    selected_owner = models.ForeignKey(        # ✅ from signup owners
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shelter_bookings_as_selected_owner",
        limit_choices_to={'user_type': 'owner'},
        null=True,
        blank=True
    )
    pet_owner_name = models.CharField(max_length=150, blank=True, null=True)  # ✅ added
    pet_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    start_date = models.DateField()
    end_date = models.DateField()
    special_instructions = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )

    def __str__(self):
        return f"{self.pet_name} ({self.selected_owner.username if self.selected_owner else 'No Owner'})"

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Shelter Booking"
        verbose_name_plural = "Shelter Bookings"


# ===================== VACCINATION BOOKING =====================
class VaccinationBooking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vaccination_bookings"
    )
    selected_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vaccination_bookings_as_selected_owner",
        limit_choices_to={'user_type': 'owner'},
        null=True,
        blank=True
    )
    pet_owner_name = models.CharField(max_length=150, blank=True, null=True)  # ✅ added
    pet_name = models.CharField(max_length=100)
    
    phone = models.CharField(max_length=15)
    vaccination_date = models.DateField()
    vaccine_type = models.CharField(max_length=100)
    special_notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )

    def __str__(self):
        return f"{self.pet_name} - {self.vaccine_type} ({self.selected_owner.username if self.selected_owner else 'No Owner'})"

    class Meta:
        ordering = ['-vaccination_date']
        verbose_name = "Vaccination Booking"
        verbose_name_plural = "Vaccination Bookings"


# ===================== GROOMING BOOKING =====================
class GroomingBooking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grooming_bookings"
    )
    selected_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grooming_bookings_as_selected_owner",
        limit_choices_to={'user_type': 'owner'},
        null=True,
        blank=True
    )
    pet_owner_name = models.CharField(max_length=150, blank=True, null=True)  # ✅ added
    pet_name = models.CharField(max_length=100)
    
    phone = models.CharField(max_length=15)
    appointment_date = models.DateField()
    special_notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )

    def __str__(self):
        return f"{self.pet_name} ({self.selected_owner.username if self.selected_owner else 'No Owner'})"

    class Meta:
        ordering = ['-appointment_date']
        verbose_name = "Grooming Booking"
        verbose_name_plural = "Grooming Bookings"


# ===== Adoption Requests =====
class AdoptionRequest(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='adoption_requests')
    adopter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='adoption_requests')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')], default='pending')
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.adopter.username} wants to adopt {self.pet.name}"

# ===== Notifications =====
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"

class Feedback(models.Model):
    FEEDBACK_TYPES = (
        ('feedback', 'Feedback'),
        ('complaint', 'Complaint'),
    )
    adopter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedbacks')
    type = models.CharField(max_length=10, choices=FEEDBACK_TYPES, default='feedback')
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)  # <-- owner reply
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.adopter.username} - {self.type}"
    

# ===== Chat System =====
class ChatRoom(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='chat_rooms')
    adopter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chat_rooms_as_adopter')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chat_rooms_as_owner')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('pet', 'adopter', 'owner')

    def __str__(self):
        return f"{self.pet.name} | {self.adopter.username} ↔ {self.owner.username}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"
