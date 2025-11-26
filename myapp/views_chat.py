from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import ChatRoom, ChatMessage, Pet
from .serializers import ChatRoomSerializer, ChatMessageSerializer

# ===== List and create chat rooms =====
class ChatRoomListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type == 'owner':
            rooms = ChatRoom.objects.filter(owner=user)
        else:
            rooms = ChatRoom.objects.filter(adopter=user)
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        pet_id = request.data.get('pet')  # ✅ match frontend
        if not pet_id:
            return Response({"error": "pet is required"}, status=400)

        pet = get_object_or_404(Pet, id=pet_id)
        adopter = request.user
        owner = pet.owner

        room, created = ChatRoom.objects.get_or_create(
            pet=pet, adopter=adopter, owner=owner
        )
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data)


# ===== List and create messages in a room =====
class ChatMessageListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        if request.user not in [room.adopter, room.owner]:
            return Response({"error": "Access denied"}, status=403)

        messages = room.messages.all().order_by('timestamp')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        if request.user not in [room.adopter, room.owner]:
            return Response({"error": "Access denied"}, status=403)

        message_text = request.data.get('message')
        if not message_text:
            return Response({"error": "Message cannot be empty"}, status=400)

        message = ChatMessage.objects.create(
            room=room,
            sender=request.user,
            message=message_text
        )
        serializer = ChatMessageSerializer(message)
        return Response(serializer.data)


# ===== Chat room detail =====
class ChatRoomDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        room = get_object_or_404(ChatRoom, id=pk)
        if request.user not in [room.adopter, room.owner]:
            return Response({"error": "Access denied"}, status=403)
        
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data)
