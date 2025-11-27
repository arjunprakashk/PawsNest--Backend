import sib_api_v3_sdk
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CustomUser, AdoptionRequest


# -----------------------------------------------------------
# 📌 Helper: Send email using Brevo API
# -----------------------------------------------------------
def send_brevo_email(to_email, subject, message):
    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        email_data = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            subject=subject,
            text_content=message,
            sender={"name": "PawsNest", "email": "noreply@pawsnest.com"}
        )

        api_instance.send_transac_email(email_data)
        print("✅ Brevo email sent to:", to_email)

    except Exception as e:
        print("❌ Brevo Email Error:", str(e))


# -----------------------------------------------------------
# 📩 Send email when admin approves an owner account
# -----------------------------------------------------------
@receiver(pre_save, sender=CustomUser)
def send_owner_approval_email(sender, instance, **kwargs):
    """
    Send email only when an owner is newly approved by admin.
    """
    if instance.pk:  # User exists
        previous = CustomUser.objects.filter(pk=instance.pk).first()

        if (
            previous
            and not previous.is_approved
            and instance.is_approved
            and instance.user_type == 'owner'
        ):
            subject = "🎉 Your Owner Account Has Been Approved!"
            message = (
                f"Hi {instance.username},\n\n"
                f"Your owner/shelter account has been approved by the admin.\n"
                f"You can now log in and start managing pets and bookings.\n\n"
                f"🐾 Welcome to PawsNest!\n\n"
                f"— The PawsNest Team"
            )

            send_brevo_email(instance.email, subject, message)


# -----------------------------------------------------------
# 🐶 Send email when owner approves adopter's adoption request
# -----------------------------------------------------------
@receiver(post_save, sender=AdoptionRequest)
def send_adoption_status_email(sender, instance, created, **kwargs):
    if created:
        return  # Do nothing on creation

    adopter_email = instance.adopter.email
    pet_name = instance.pet.name
    owner = instance.pet.owner
    owner_name = getattr(owner, "name", owner.username)
    owner_email = owner.email
    owner_contact = getattr(owner, "contact", "Not provided")

    # Approved
    if instance.status == "approved":
        subject = f"🎉 Adoption Approved for {pet_name}!"
        message = (
            f"Hi {instance.adopter.username},\n\n"
            f"Your adoption request for '{pet_name}' has been approved by {owner_name}.\n\n"
            f"Owner Contact:\n"
            f"📧 Email: {owner_email}\n"
            f"📞 Phone: {owner_contact}\n\n"
            f"Thank you for adopting a pet ❤️\n\n"
            f"— The PawsNest Team"
        )

    # Rejected
    elif instance.status == "rejected":
        subject = f"😿 Adoption Request Rejected for {pet_name}"
        message = (
            f"Hi {instance.adopter.username},\n\n"
            f"Your adoption request for '{pet_name}' was not approved.\n\n"
            f"Please try adopting another pet ❤️\n\n"
            f"— The PawsNest Team"
        )

    else:
        return  # Pending / unchanged

    send_brevo_email(adopter_email, subject, message)
