from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Pet,
    Notification,
    ShelterBooking,
    VaccinationBooking,
    GroomingBooking,
    AdoptionRequest,
    CustomUser,
    Feedback,
    ChatRoom,
    ChatMessage
)

User = get_user_model()

# ===============================
# 🔹 AUTH SERIALIZERS
# ===============================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type', 'name', 'location', 'contact']

    def create(self, validated_data):
        user_type = validated_data.get('user_type', 'adopter')
        validated_data['is_approved'] = True if user_type == 'adopter' else False

        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=[('adopter', 'Adopter'), ('owner', 'Owner'), ('admin', 'Admin')])


# ===============================
# 🔹 PET + ADOPTION SERIALIZERS
# ===============================
class AdoptionRequestSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source="pet.name", read_only=True)
    adopter = serializers.CharField(source="adopter.username", read_only=True)
    pet_owner = serializers.CharField(source="pet.owner.username", read_only=True)
    pet = serializers.PrimaryKeyRelatedField(queryset=Pet.objects.all(), write_only=True)

    class Meta:
        model = AdoptionRequest
        fields = ["id", "pet", "pet_name", "adopter", "pet_owner", "message", "status"]


class PetSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    adoption_requests = AdoptionRequestSerializer(many=True, read_only=True)
    is_adopted = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = [
            "id", "name", "age", "breed", "gender", "size",
            "description", "image", "location", "owner", "owner_name",
            "owner_id", "contact", "is_adopted", "adoption_requests",
        ]

    def get_is_adopted(self, obj):
        return obj.adoption_requests.filter(status='approved').exists()


# ===============================
# 🔹 OWNER MINI SERIALIZER
# ===============================
class OwnerMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'email', 'location', 'contact']


# ===============================
## ===============================
# 🔹 BOOKING SERIALIZERS (Updated)
# ===============================
from rest_framework import serializers
from .models import ShelterBooking, VaccinationBooking, GroomingBooking, CustomUser
from .serializers import OwnerMiniSerializer  


# Shelter Booking Serializer
class ShelterBookingSerializer(serializers.ModelSerializer):
    selected_owner = OwnerMiniSerializer(read_only=True)
    selected_owner_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(user_type='owner', is_approved=True),
        source='selected_owner',
        write_only=True
    )

    user_name = serializers.CharField(source='user.username', read_only=True)
    selected_owner_name = serializers.CharField(source='selected_owner.username', read_only=True)

    class Meta:
        model = ShelterBooking
        fields = [
            'id',
            'user', 'user_name',
            'selected_owner', 'selected_owner_id', 'selected_owner_name',
            'pet_owner_name', 'pet_name', 'phone',
            'start_date', 'end_date', 'special_instructions',
            'status',
        ]
        read_only_fields = ['user']


# ✅ Vaccination Booking Serializer (fixed)
class VaccinationBookingSerializer(serializers.ModelSerializer):
    selected_owner = OwnerMiniSerializer(read_only=True)
    selected_owner_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(user_type='owner', is_approved=True),
        source='selected_owner',
        write_only=True
    )

    class Meta:
        model = VaccinationBooking
        fields = '__all__'   # ✅ added this line
        read_only_fields = ['user']


# ✅ Grooming Booking Serializer (fixed)
class GroomingBookingSerializer(serializers.ModelSerializer):
    selected_owner = OwnerMiniSerializer(read_only=True)
    selected_owner_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(user_type='owner', is_approved=True),
        source='selected_owner',
        write_only=True
    )

    class Meta:
        model = GroomingBooking
        fields = '__all__'   # ✅ added this line
        read_only_fields = ['user']


# ===============================
# 🔹 NOTIFICATION + OWNER + FEEDBACK
# ===============================
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'name', 'location', 'contact', 'is_approved']


class FeedbackSerializer(serializers.ModelSerializer):
    adopter_name = serializers.CharField(source="adopter.username", read_only=True)

    class Meta:
        model = Feedback
        fields = ["id", "adopter", "adopter_name", "type", "message", "reply", "created_at"]
        read_only_fields = ["adopter", "created_at"]


# ===============================
# 🔹 CHAT SERIALIZERS
# ===============================
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'user_type']


class PetMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ['id', 'name', 'image']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'message', 'timestamp', 'is_read']


class ChatRoomSerializer(serializers.ModelSerializer):
    pet = PetMiniSerializer(read_only=True)
    adopter = UserMiniSerializer(read_only=True)
    owner = UserMiniSerializer(read_only=True)
    adopter_name = serializers.CharField(source='adopter.username', read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    pet_name = serializers.CharField(source='pet.name', read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'pet', 'adopter', 'owner',
            'adopter_name', 'owner_name', 'pet_name', 'created_at'
        ]


#----------------Password Reset -----------------
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


# Request Password Reset
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value


# Set New Password
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    token = serializers.CharField()
    user_id = serializers.IntegerField()

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        token = attrs.get('token')
        password = attrs.get('password')

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid user ID.")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired token.")

        user.set_password(password)
        user.save()
        return attrs
