from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import PasswordResetSerializer, SetNewPasswordSerializer

User = get_user_model()  # ✅ Use your custom user model


# -------------------------------
# Request Password Reset
# -------------------------------
class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]  # ✅ Unauthenticated access allowed

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)

        # ✅ Correct frontend URL for Vite (port 5173)
        reset_link = f"http://localhost:5173/reset-password/{user.pk}/{token}/"

        send_mail(
            'Password Reset Request',
            f'Hello {user.username},\n\n'
            f'Click the link below to reset your password:\n\n{reset_link}\n\n'
            f'If you did not request this, you can safely ignore this email.',
            'pawsnest@example.com',
            [email],
            fail_silently=False,
        )

        return Response(
            {"message": "Password reset link sent to your email."},
            status=status.HTTP_200_OK,
        )


# -------------------------------
# Confirm Password Reset
# -------------------------------
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "Password reset successful!"}, status=status.HTTP_200_OK
        )
