# utils/pdf_generator.py
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def generate_booking_pdf(booking, booking_type):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # 🎨 Choose theme color based on booking type
    color_map = {
        "shelter": colors.HexColor("#4B9CD3"),      # blue
        "vaccination": colors.HexColor("#0084FF"),  # green
        "grooming": colors.HexColor("#0088FF"),     # orange
    }
    theme_color = color_map.get(booking_type.lower(), colors.HexColor("#6A1B9A"))

    # ===== HEADER BAR =====
    p.setFillColor(theme_color)
    p.rect(0, height - 100, width, 100, fill=1, stroke=0)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 22)
    p.drawCentredString(width / 2, height - 60, f"{booking_type.title()} Booking Confirmation")

    # ===== BODY =====
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 12)
    y = height - 140

    # Section Title
    p.setFillColor(theme_color)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(80, y, "📋 Booking Details")
    y -= 15
    p.setStrokeColor(theme_color)
    p.line(80, y, width - 80, y)
    y -= 20

    # Common details
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 12)
    info = [
        ("Booking ID", booking.id),
        ("Adopter", booking.user.username),
        ("Owner", getattr(booking.selected_owner, 'username', 'N/A')),
        ("Pet Name", booking.pet_name),
        ("Pet Owner Name", booking.pet_owner_name or "N/A"),
        ("Email", booking.user.email or "N/A"),
        ("Phone", booking.phone),
    ]

    for label, value in info:
        p.drawString(100, y, f"{label}: {value}")
        y -= 20

    y -= 10
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(theme_color)
    p.drawString(80, y, "📅 Booking Specifics")
    y -= 15
    p.setStrokeColor(theme_color)
    p.line(80, y, width - 80, y)
    y -= 20

    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)

    # Type-specific info
    if booking_type.lower() == "shelter":
        p.drawString(100, y, f"Start Date: {booking.start_date}"); y -= 20
        p.drawString(100, y, f"End Date: {booking.end_date}"); y -= 20

    elif booking_type.lower() == "vaccination":
        p.drawString(100, y, f"Vaccination Date: {booking.vaccination_date}"); y -= 20
        p.drawString(100, y, f"Vaccine Type: {booking.vaccine_type}"); y -= 20

    elif booking_type.lower() == "grooming":
        p.drawString(100, y, f"Appointment Date: {booking.appointment_date}"); y -= 20
        p.drawString(100, y, f"Special Notes: {booking.special_notes or 'N/A'}"); y -= 20

    # ===== STATUS BOX =====
    y -= 10
    p.setFillColor(theme_color)
    p.roundRect(80, y - 40, width - 160, 40, 10, fill=1, stroke=0)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 13)
    p.drawCentredString(width / 2, y - 20, "✅ STATUS: CONFIRMED")

    # ===== FOOTER =====
    p.setFillColor(colors.gray)
    p.setFont("Helvetica-Oblique", 11)
    p.drawCentredString(width / 2, 60, "Thank you for choosing PawsNest! 🐾")
    p.drawCentredString(width / 2, 45, "Your trust keeps tails wagging ❤️")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
