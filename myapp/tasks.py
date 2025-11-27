import sib_api_v3_sdk
from celery import shared_task
from django.conf import settings

@shared_task
def send_booking_email_task(subject, message, recipient):
    try:
        # Setup Brevo config
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        # Prepare email
        email_data = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": recipient}],
            subject=subject,
            text_content=message,
            sender={"name": "PawsNest", "email": "noreply@pawsnest.com"}
        )

        # Send email
        api_instance.send_transac_email(email_data)

        return f"Email sent to {recipient}"

    except Exception as e:
        return f"Error sending email: {str(e)}"
