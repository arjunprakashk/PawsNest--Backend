from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes, action
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Pet,ShelterBooking, VaccinationBooking, GroomingBooking,
    AdoptionRequest, Notification, CustomUser
)
from .serializers import (
    RegisterSerializer,PetSerializer, ShelterBookingSerializer,
    VaccinationBookingSerializer, GroomingBookingSerializer,
    AdoptionRequestSerializer, NotificationSerializer, OwnerSerializer,
    
)
from myapp import serializers

User = get_user_model()

# ---------------------- REGISTER ----------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if data.get("user_type") in ["owner"]:
            data["is_approved"] = False
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Signup successful! Please wait for admin approval if owner."},
            status=status.HTTP_201_CREATED
        )

# ---------------------- LOGIN ----------------------
from django.contrib.auth import authenticate, get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


from django.contrib.auth import authenticate, get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("email")  # can be email or username
        password = request.data.get("password")
        User = get_user_model()

        user = None

        # ✅ Try authenticating as email first
        try:
            user_obj = User.objects.get(email=identifier)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            # ✅ If not found, try authenticating as username (for admin)
            user = authenticate(username=identifier, password=password)

        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ Check owner approval
        if user.user_type == "owner" and not user.is_approved:
            return Response(
                {"error": "Your account has not been approved by admin yet."},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ JWT token generation
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "username": user.username,
            "user_type": user.user_type
        })


# ---------------------- CURRENT USER ----------------------
class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "user_type": user.user_type
        })

# ---------------------- ADMIN DASHBOARD & OWNER APPROVAL ----------------------
class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type != "admin":
            return Response({"error": "Only admin can access this"}, status=status.HTTP_403_FORBIDDEN)

        total_users = User.objects.filter(user_type='adopter').count() + User.objects.filter(user_type='owner').count()
        total_owners = User.objects.filter(user_type='owner').count()
        total_pets = Pet.objects.count()

        return Response({
            "totalUsers": total_users,
            "totalOwners": total_owners,
            "totalPets": total_pets
        })

class PendingOwnersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type != "admin":
            return Response({"error": "Only admin can access this"}, status=status.HTTP_403_FORBIDDEN)

        pending_owners = User.objects.filter(user_type='owner', is_approved=False)
        data = [{
            "id": o.id,
            "username": o.username,
            "email": o.email,
            "name": o.name,
            "location": o.location,
            "contact": o.contact
        } for o in pending_owners]
        return Response(data)

class ApproveOwnerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, owner_id):
        user = request.user
        if user.user_type != "admin":
            return Response({"error": "Only admin can approve owners"}, status=status.HTTP_403_FORBIDDEN)

        try:
            owner = User.objects.get(id=owner_id, user_type='owner')
            owner.is_approved = True
            owner.save()
            return Response({"message": f"{owner.username} has been approved."})
        except User.DoesNotExist:
            return Response({"error": "Owner not found"}, status=status.HTTP_404_NOT_FOUND)

# ---------------------- ALL OWNERS (FOR ADMIN) ----------------------
@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_owners(request):
    owners = User.objects.filter(user_type='owner')
    serializer = OwnerSerializer(owners, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_owner(request, owner_id):
    try:
        owner = User.objects.get(id=owner_id, user_type='owner')
        owner.delete()
        return Response({"message": "Owner deleted successfully."})
    except User.DoesNotExist:
        return Response({"error": "Owner not found."}, status=404)

# ---------------------- PETS ----------------------
class PetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]  # default permission

    def get_queryset(self):
        user = self.request.user
        if self.action in ["list", "retrieve"]:
            # Only return pets owned by the user if they are an owner
            if user.user_type == "owner":
                return Pet.objects.filter(owner=user).order_by('-created_at')
            return Pet.objects.all().order_by('-created_at')
        return Pet.objects.filter(owner=user)  # only owners can update/delete their pets

    def perform_create(self, serializer):
        if self.request.user.user_type != "owner":
            raise PermissionError("Only owners/shelters can add pets")
        serializer.save(owner=self.request.user)
# ---------------------- IMPORTS ----------------------
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import (
    CustomUser,
    ShelterBooking,
    VaccinationBooking,
    GroomingBooking,
    Notification
)
from .serializers import (
    ShelterBookingSerializer,
    VaccinationBookingSerializer,
    GroomingBookingSerializer,
    OwnerSerializer,
    OwnerMiniSerializer
)

# ---------------------- OWNER LIST (for adopter dropdown) ----------------------
class OwnerListView(generics.ListAPIView):
    """List of approved owners/shelters for adopters to choose from."""
    queryset = CustomUser.objects.filter(user_type="owner", is_approved=True)
    serializer_class = OwnerSerializer
    permission_classes = [AllowAny]


# ---------------------- SHELTER BOOKING ----------------------
from django.core.mail import EmailMessage
from django.conf import settings
from utils.pdf_generator import generate_booking_pdf  # ✅ import your PDF helper

class ShelterBookingView(viewsets.ModelViewSet):
    serializer_class = ShelterBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "owner":
            return ShelterBooking.objects.filter(selected_owner=user).order_by('-start_date')
        elif user.user_type == "adopter":
            return ShelterBooking.objects.filter(user=user).order_by('-start_date')
        elif user.user_type in ["admin"] or user.is_staff:
            return ShelterBooking.objects.all().order_by('-start_date')
        return ShelterBooking.objects.none()

    def perform_create(self, serializer):
        selected_owner_id = self.request.data.get("selected_owner_id")
        pet_owner_name = self.request.data.get("pet_owner_name")

        selected_owner = None
        if selected_owner_id:
            try:
                selected_owner = CustomUser.objects.get(
                    id=selected_owner_id,
                    user_type="owner",
                    is_approved=True
                )
            except CustomUser.DoesNotExist:
                pass

        booking = serializer.save(
            user=self.request.user,
            selected_owner=selected_owner,
            pet_owner_name=pet_owner_name,
            status="approved"  # ✅ auto-approved
        )

        # Notify the owner
        if selected_owner:
            Notification.objects.create(
                user=selected_owner,
                message=f"New shelter booking for {booking.pet_name} has been approved."
            )

        # =================== EMAIL WITH PDF ATTACHMENT ===================
        adopter_email = booking.user.email
        owner_email = selected_owner.email if selected_owner else None

        if adopter_email:
            try:
                # ✅ Generate PDF using your utility
                pdf_buffer = generate_booking_pdf(booking, "Shelter")

                email_subject = "Shelter Booking Confirmed"
                email_body = (
                    f"Dear {booking.user.username},\n\n"
                    f"Your shelter booking for {booking.pet_name} has been confirmed.\n"
                    f"Start Date: {booking.start_date}\n"
                    f"End Date: {booking.end_date}\n\n"
                    f"Thank you for choosing our service!\n\n"
                    f"- PawsNest Team 🐾"
                )

                # ✅ Create email with PDF
                email = EmailMessage(
                    subject=email_subject,
                    body=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[adopter_email],
                    cc=[owner_email] if owner_email else None,
                )

                email.attach(
                    f"shelter_booking_{booking.id}.pdf",
                    pdf_buffer.getvalue(),
                    "application/pdf"
                )
                email.send(fail_silently=True)

            except Exception as e:
                print(f"Email send failed: {e}")
# ---------------------- VACCINATION BOOKING ----------------------
from django.core.mail import EmailMessage
from django.conf import settings
from utils.pdf_generator import generate_booking_pdf  # ✅ your existing helper

class VaccinationBookingView(viewsets.ModelViewSet):
    serializer_class = VaccinationBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "owner":
            return VaccinationBooking.objects.filter(selected_owner=user).order_by('-vaccination_date')
        elif user.user_type == "adopter":
            return VaccinationBooking.objects.filter(user=user).order_by('-vaccination_date')
        elif user.user_type in ["admin"] or user.is_staff:
            return VaccinationBooking.objects.all().order_by('-vaccination_date')
        return VaccinationBooking.objects.none()

    def perform_create(self, serializer):
        selected_owner_id = (
            self.request.data.get("selected_owner_id")
            or self.request.data.get("selected_owner")
        )
        pet_owner_name = self.request.data.get("pet_owner_name")

        selected_owner = None
        if selected_owner_id:
            try:
                selected_owner = CustomUser.objects.get(
                    id=selected_owner_id,
                    user_type="owner",
                    is_approved=True
                )
            except CustomUser.DoesNotExist:
                pass

        booking = serializer.save(
            user=self.request.user,
            selected_owner=selected_owner,
            pet_owner_name=pet_owner_name,
            status="approved"  # ✅ auto-approved
        )

        # Notify owner
        if selected_owner:
            Notification.objects.create(
                user=selected_owner,
                message=f"New vaccination booking for {booking.pet_name} has been approved."
            )

        # =================== EMAIL WITH PDF ATTACHMENT ===================
        adopter_email = booking.user.email
        owner_email = selected_owner.email if selected_owner else None

        if adopter_email:
            try:
                # ✅ Generate PDF using your existing function
                pdf_buffer = generate_booking_pdf(booking, "Vaccination")

                email_subject = "Vaccination Booking Confirmed"
                email_body = (
                    f"Dear {booking.user.username},\n\n"
                    f"Your vaccination booking for {booking.pet_name} has been confirmed.\n"
                    f"Date: {booking.vaccination_date}\n"
                    f"Vaccine Type: {booking.vaccine_type}\n\n"
                    f"Thank you for trusting PawsNest!\n\n"
                    f"- PawsNest Team 🐾"
                )

                # ✅ Send email
                email = EmailMessage(
                    subject=email_subject,
                    body=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[adopter_email],
                    cc=[owner_email] if owner_email else None,
                )

                email.attach(
                    f"vaccination_booking_{booking.id}.pdf",
                    pdf_buffer.getvalue(),
                    "application/pdf"
                )
                email.send(fail_silently=True)

            except Exception as e:
                print(f"Email send failed: {e}")



# ---------------------- GROOMING BOOKING ----------------------
from django.core.mail import EmailMessage
from django.conf import settings
from utils.pdf_generator import generate_booking_pdf  # ✅ your existing PDF utility

class GroomingBookingView(viewsets.ModelViewSet):
    serializer_class = GroomingBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "owner":
            return GroomingBooking.objects.filter(selected_owner=user).order_by('-appointment_date')
        elif user.user_type == "adopter":
            return GroomingBooking.objects.filter(user=user).order_by('-appointment_date')
        elif user.user_type in ["admin"] or user.is_staff:
            return GroomingBooking.objects.all().order_by('-appointment_date')
        return GroomingBooking.objects.none()

    def perform_create(self, serializer):
        selected_owner_id = (
            self.request.data.get("selected_owner_id")
            or self.request.data.get("selected_owner")
        )
        pet_owner_name = self.request.data.get("pet_owner_name")

        selected_owner = None
        if selected_owner_id:
            try:
                selected_owner = CustomUser.objects.get(
                    id=selected_owner_id,
                    user_type="owner",
                    is_approved=True
                )
            except CustomUser.DoesNotExist:
                pass

        booking = serializer.save(
            user=self.request.user,
            selected_owner=selected_owner,
            pet_owner_name=pet_owner_name,
            status="approved"  # ✅ auto-approved
        )

        # ✅ Notify owner (inside app only, not by email)
        if selected_owner:
            Notification.objects.create(
                user=selected_owner,
                message=f"New grooming booking for {booking.pet_name} has been approved."
            )

        # =================== EMAIL TO ADOPTER WITH PDF ===================
        adopter_email = booking.user.email

        if adopter_email:
            try:
                pdf_buffer = generate_booking_pdf(booking, "Grooming")

                email_subject = "Grooming Booking Confirmed"
                email_body = (
                    f"Dear {booking.user.username},\n\n"
                    f"Your grooming booking for {booking.pet_name} has been confirmed.\n"
                    f"Appointment Date: {booking.appointment_date}\n\n"
                    f"Thank you for choosing our grooming service!\n\n"
                    f"- PawsNest Team 🐾"
                )

                # ✅ Send only to adopter (no CC)
                email = EmailMessage(
                    subject=email_subject,
                    body=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[adopter_email],
                )

                email.attach(
                    f"grooming_booking_{booking.id}.pdf",
                    pdf_buffer.getvalue(),
                    "application/pdf"
                )
                email.send(fail_silently=True)

            except Exception as e:
                print(f"Email send failed: {e}")

        # =================== EMAIL WITH PDF ATTACHMENT ===================
        adopter_email = booking.user.email
        owner_email = selected_owner.email if selected_owner else None

        if adopter_email:
            try:
                # ✅ Generate PDF (no service_type needed)
                pdf_buffer = generate_booking_pdf(booking, "Grooming")

                email_subject = "Grooming Booking Confirmed"
                email_body = (
                    f"Dear {booking.user.username},\n\n"
                    f"Your grooming booking for {booking.pet_name} has been confirmed.\n"
                    f"Appointment Date: {booking.appointment_date}\n\n"
                    f"Thank you for choosing our grooming service!\n\n"
                    f"- PawsNest Team 🐾"
                )

                email = EmailMessage(
                    subject=email_subject,
                    body=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[adopter_email],
                    cc=[owner_email] if owner_email else None,
                )

                email.attach(
                    f"grooming_booking_{booking.id}.pdf",
                    pdf_buffer.getvalue(),
                    "application/pdf"
                )
                email.send(fail_silently=True)

            except Exception as e:
                print(f"Email send failed: {e}")

# ---------------------- ADOPTION REQUESTS ----------------------
class AdoptionRequestViewSet(viewsets.ModelViewSet):
    queryset = AdoptionRequest.objects.all().order_by('-request_date')
    serializer_class = AdoptionRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        adoption_request = serializer.save(adopter=self.request.user)
        Notification.objects.create(
            user=adoption_request.pet.owner,
            message=f"{adoption_request.adopter.username} wants to adopt {adoption_request.pet.name}!"
        )

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def respond(self, request, pk=None):
        adoption_request = self.get_object()
        user = request.user
        if adoption_request.pet.owner != user:
            return Response({"error": "Only pet owner can respond"}, status=status.HTTP_403_FORBIDDEN)

        action_type = request.data.get("action")
        if action_type not in ["approve", "reject"]:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        adoption_request.status = "approved" if action_type == "approve" else "rejected"
        adoption_request.save()

        Notification.objects.create(
            user=adoption_request.adopter,
            message=f"Your adoption request for {adoption_request.pet.name} was {adoption_request.status}!"
        )
        return Response({"message": f"Request {adoption_request.status} successfully."})

# ---------------------- NOTIFICATIONS ----------------------
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

# ---------------------- UPDATE CURRENT USER PROFILE ----------------------
class UpdateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "user_type": user.user_type,
            "name": user.name,
            "location": user.location,
            "contact": user.contact
        })

    def patch(self, request):
        user = request.user
        data = request.data
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.name = data.get("name", user.name)
        user.location = data.get("location", user.location)
        user.contact = data.get("contact", user.contact)
        if data.get("password"):
            user.set_password(data.get("password"))
        user.save()
        return Response({"message": "Profile updated successfully!"})


from .models import Feedback
from .serializers import FeedbackSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

# views.py
from rest_framework.decorators import action

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-created_at')
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(adopter=self.request.user)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def reply(self, request, pk=None):
        feedback = self.get_object()
        if request.user.user_type != "owner":
            return Response({"error": "Only owners can reply"}, status=403)

        reply_text = request.data.get("reply", "")
        if not reply_text:
            return Response({"error": "Reply cannot be empty"}, status=400)

        feedback.reply = reply_text
        feedback.save()
        return Response({"message": "Reply sent successfully!", "reply": feedback.reply})
    