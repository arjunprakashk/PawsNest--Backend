import razorpay
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ <--- Add this line
def create_razorpay_order(request):
    try:
        amount = int(request.data.get("amount", 500)) * 100  # Amount in paise
        receipt = request.data.get("receipt", "order_rcptid_11")
        notes = request.data.get("notes", {})

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": receipt,
            "payment_capture": 1,
            "notes": notes
        })

        return Response({
            "order": order,
            "key_id": settings.RAZORPAY_KEY_ID
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)
