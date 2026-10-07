from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from reportlab.pdfgen import canvas


BASE_DIR = Path(__file__).resolve().parent.parent.parent

TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "generated"

OUTPUT_DIR.mkdir(exist_ok=True)


jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR)
)


def generate_certificate(
    certificate_id: int,
    recipient_name: str,
    event_name: str,
    organization: str,
    event_date: str
) -> str:

    template = jinja_env.get_template("certificate_template.html")

    template_data = {
        "recipient_name": recipient_name,
        "event_name": event_name,
        "organization": organization,
        "event_date": event_date
    }

    template.render(**template_data)

    file_path = OUTPUT_DIR / f"certificate_{certificate_id}.pdf"

    pdf = canvas.Canvas(
        str(file_path),
        pagesize=(595, 842)
    )

    pdf.setTitle("Certificate of Participation")

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(
        297,
        720,
        "Certificate of Participation"
    )

    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        297,
        670,
        "This certificate is proudly presented to"
    )

    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawCentredString(
        297,
        610,
        template_data["recipient_name"]
    )

    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        297,
        550,
        f"for successfully participating in {template_data['event_name']}"
    )

    pdf.drawCentredString(
        297,
        520,
        f"Organized by {template_data['organization']}"
    )

    pdf.drawCentredString(
        297,
        490,
        f"Date: {template_data['event_date']}"
    )

    pdf.save()

    return str(file_path)