from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, AdoptionRequest

# -----------------------------------------------------------
# 📩 Send email when admin approves an owner account
# -----------------------------------------------------------
@receiver(pre_save, sender=CustomUser)
def send_owner_approval_email(sender, instance, **kwargs):
    """
    Send email only when an owner is newly approved by admin.
    """
    if instance.pk:  # existing user
        previous = CustomUser.objects.filter(pk=instance.pk).first()
        if (
            previous
            and previous.is_approved is False
            and instance.is_approved is True
            and instance.user_type == 'owner'
        ):
            subject = "🎉 Your Account Has Been Approved!"
            message = (
                f"Hi {instance.username},\n\n"
                f"Great news! Your shelter account has been approved by the admin.\n"
                f"You can now log in to your account and start managing pets and bookings.\n\n"
                f"🐾 Welcome to PawsNest!\n\n"
                f"— The PawsNest Team"
            )
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=False,
                )
                print(f"✅ Sent owner approval email to {instance.email}")
            except Exception as e:
                print("❌ Error sending owner approval email:", e)


# -----------------------------------------------------------
# 🐶 Send email when owner approves adopter's adoption request
# -----------------------------------------------------------
@receiver(post_save, sender=AdoptionRequest)
def send_adoption_status_email(sender, instance, created, **kwargs):
    """
    Sends email to the adopter when their adoption request is approved or rejected.
    """
    if created:
        return  # skip on creation

    adopter_email = instance.adopter.email
    pet_name = instance.pet.name
    owner = instance.pet.owner
    owner_name = getattr(owner, "name", owner.username)
    owner_email = owner.email
    owner_contact = getattr(owner, "contact", "Not provided")

    # ✅ If approved
    if instance.status == "approved":
        subject = f"🎉 Your adoption request for {pet_name} has been approved!"
        message = (
            f"Dear {instance.adopter.username},\n\n"
            f"Good news! Your adoption request for '{pet_name}' has been approved by {owner_name}.\n\n"
            f"You can now contact the owner for further details:\n"
            f"📧 Email: {owner_email}\n"
            f"📞 Contact: {owner_contact}\n\n"
            f"Thank you for choosing to adopt — you're giving a pet a loving home ❤️\n\n"
            f"– The PawsNest Team"
        )

    # ❌ If rejected
    elif instance.status == "rejected":
        subject = f"😿 Your adoption request for {pet_name} has been rejected"
        message = (
            f"Dear {instance.adopter.username},\n\n"
            f"We're sorry to inform you that your adoption request for '{pet_name}' "
            f"was not approved by {owner_name}.\n\n"
            f"Don't be discouraged — there are many other pets looking for a loving home! 💕\n"
            f"You can browse other available pets on our platform anytime.\n\n"
            f"— The PawsNest Team"
        )

    else:
        return  # do nothing if status is 'pending' or unchanged

    # Send email
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [adopter_email],
            fail_silently=False,
        )
        print(f"✅ Sent adoption status email ({instance.status}) to {adopter_email}")
    except Exception as e:
        print("❌ Error sending adoption status email:", e)
