from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginAPIView, CurrentUserAPIView,
    PetViewSet, ShelterBookingView, VaccinationBookingView,
    GroomingBookingView, AdoptionRequestViewSet, NotificationViewSet,
    AdminDashboardAPIView, PendingOwnersAPIView, ApproveOwnerAPIView,
    UpdateProfileAPIView, all_owners, delete_owner, FeedbackViewSet,
    OwnerListView  
)
from .views_chat import ChatRoomListCreateView, ChatMessageListCreateView, ChatRoomDetailView
from .views_email import send_booking_email
from .views_password import PasswordResetView, PasswordResetConfirmView
from .views_chatbot import chatbot_response


# Router
router = DefaultRouter()
router.register(r'pets', PetViewSet, basename='pet')
router.register(r'shelter-bookings', ShelterBookingView, basename='shelter-booking')
router.register(r'vaccination-bookings', VaccinationBookingView, basename='vaccination-booking')
router.register(r'grooming-bookings', GroomingBookingView, basename='grooming-booking')
router.register(r'adoption-requests', AdoptionRequestViewSet, basename='adoption-request')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/me/', CurrentUserAPIView.as_view(), name='current_user'),
    path('auth/profile/', UpdateProfileAPIView.as_view(), name='update_profile'),

    # Admin
    path('admin/dashboard/', AdminDashboardAPIView.as_view(), name='admin_dashboard'),
    path('admin/pending-owners/', PendingOwnersAPIView.as_view(), name='pending_owners'),
    path('admin/approve-owner/<int:owner_id>/', ApproveOwnerAPIView.as_view(), name='approve_owner'),
    path('admin/owners/', all_owners, name='all_owners'),
    path('admin/delete-owner/<int:owner_id>/', delete_owner, name='delete_owner'),
    path('email/send-booking/', send_booking_email, name='send_booking_email'),

    #Reset Password
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # 🟩 Owner List (for dropdown in bookings)
    path('owners/', OwnerListView.as_view(), name='owner-list'),


    # Router
    path('', include(router.urls)),

    # ===== Chat URLs =====
    path('chatrooms/', ChatRoomListCreateView.as_view(), name='chatroom-list'),
    path('chatrooms/<int:pk>/', ChatRoomDetailView.as_view(), name='chatroom-detail'),
    path('chatrooms/<int:room_id>/messages/', ChatMessageListCreateView.as_view(), name='chatroom-messages'),

    #Chat Bot
    path("chatbot/", chatbot_response, name="chatbot_response"),


]



