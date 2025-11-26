from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.apps import apps

from myapp.tasks import send_booking_email_task   # <-- Celery Task Import


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_booking_email(request):
    """
    Send email to the adopter (based on the user who made the booking),
    now using Celery for background processing.
    """
    try:
        booking_id = request.data.get('booking_id')
        booking_type = request.data.get('booking_type')
        subject = request.data.get('subject', 'Booking Update')
        message = request.data.get('message', '')
        owner_name = request.user.username

        if not booking_id or not booking_type:
            return Response({'error': 'Missing booking_id or booking_type'}, status=400)

        # Map booking type to model names
        model_map = {
            'shelter': 'ShelterBooking',
            'grooming': 'GroomingBooking',
            'vaccination': 'VaccinationBooking',
        }

        model_name = model_map.get(booking_type.lower())
        if not model_name:
            return Response({'error': 'Invalid booking type'}, status=400)

        # Correct app name should be "myapp"
        BookingModel = apps.get_model('myapp', model_name)

        booking = BookingModel.objects.filter(id=booking_id).first()
        if not booking:
            return Response({'error': 'Booking not found'}, status=404)

        # Get adopter's email
        recipient_email = getattr(booking.user, "email", None)
        if not recipient_email:
            return Response({'error': 'No email found for this booking’s user'}, status=400)

        # Prepare full message
        full_message = f"From {owner_name}:\n\n{message}"

        # 🚀 SEND EMAIL USING CELERY (background task)
        send_booking_email_task.delay(
            subject,
            full_message,
            recipient_email
        )

        return Response({'success': f'Email is being sent to {recipient_email} (via Celery)'})

    except Exception as e:
        return Response({'error': str(e)}, status=500)
