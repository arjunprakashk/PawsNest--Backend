from django.contrib import admin
from .models import (
    CustomUser,
    Pet,
    ShelterBooking,
    VaccinationBooking,
    GroomingBooking,
    AdoptionRequest,
    Notification,
    Feedback,
    ChatRoom,
    ChatMessage
)

# ==========================
# 🔹 CustomUser Admin
# ==========================
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'user_type', 'is_approved', 'is_staff')
    list_filter = ('user_type', 'is_approved', 'is_staff')
    search_fields = ('username', 'email', 'name', 'location', 'contact')
    ordering = ('id',)

    # Allow editing directly from list
    list_editable = ('is_approved',)

    # Show approval checkbox inside user edit page
    fields = (
        'username',
        'email',
        'user_type',
        'name',
        'location',
        'contact',
        'is_approved',
        'is_staff',
        'is_superuser',
        'password',
    )

    # Add action button
    actions = ('approve_owners',)

    def approve_owners(self, request, queryset):
        owners = queryset.filter(user_type='owner')
        count = owners.update(is_approved=True)
        self.message_user(request, f"{count} owner(s) approved successfully!")
    approve_owners.short_description = "Approve selected owners"



# ==========================
# 🔹 Pet Admin
# ==========================
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'breed', 'gender', 'size', 'is_adopted', 'created_at')
    list_filter = ('gender', 'size', 'is_adopted')
    search_fields = ('name', 'breed', 'owner__username')
    ordering = ('-created_at',)


# ==========================
# 🔹 Shelter Booking Admin
# ==========================
@admin.register(ShelterBooking)
class ShelterBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet_name', 'user', 'selected_owner', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('pet_name', 'user__username', 'selected_owner__username', 'email', 'phone')
    ordering = ('-start_date',)


# ==========================
# 🔹 Vaccination Booking Admin
# ==========================
@admin.register(VaccinationBooking)
class VaccinationBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet_name', 'user', 'selected_owner', 'vaccination_date', 'vaccine_type', 'status')
    list_filter = ('status', 'vaccination_date')
    search_fields = ('pet_name', 'vaccine_type', 'user__username', 'selected_owner__username')
    ordering = ('-vaccination_date',)


# ==========================
# 🔹 Grooming Booking Admin
# ==========================
@admin.register(GroomingBooking)
class GroomingBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet_name', 'user', 'selected_owner', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('pet_name', 'user__username', 'selected_owner__username')
    ordering = ('-appointment_date',)


# ==========================
# 🔹 Adoption Request Admin
# ==========================
@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet', 'adopter', 'status', 'request_date')
    list_filter = ('status', 'request_date')
    search_fields = ('pet__name', 'adopter__username')
    ordering = ('-request_date',)


# ==========================
# 🔹 Notification Admin
# ==========================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)


# ==========================
# 🔹 Feedback Admin
# ==========================
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'adopter', 'type', 'message', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('adopter__username', 'message')
    ordering = ('-created_at',)


# ==========================
# 🔹 ChatRoom Admin
# ==========================
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet', 'adopter', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('pet__name', 'adopter__username', 'owner__username')
    ordering = ('-created_at',)


# ==========================
# 🔹 ChatMessage Admin
# ==========================
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'message', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'message', 'room__pet__name')
    ordering = ('-timestamp',)
