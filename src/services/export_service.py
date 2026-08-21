import csv
from datetime import datetime
from io import BytesIO,StringIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import grey
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether
)




def generate_pdf(user, saved_jobs):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading = styles["Heading2"]
    normal = styles["BodyText"]

    elements = []

    elements.append(Paragraph("JobFlow Export", title_style))
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}",
            normal
        )
    )

    elements.append(
        Paragraph(
            f"User: {user.email}",
            normal
        )
    )

    elements.append(
        Paragraph(
            f"Total Saved Jobs: {len(saved_jobs)}",
            normal
        )
    )

    elements.append(Spacer(1, 15))

    for saved_job in saved_jobs:

        job_elements= []

        job_elements.append(HRFlowable(color=grey))

        job_elements.append(Spacer(1, 10))

        job_elements.append(Paragraph(saved_job.job.title, heading))

        job_elements.append(
            Paragraph(f"<b>Company:</b> {saved_job.job.company}", normal)
        )

        job_elements.append(
            Paragraph(f"<b>Location:</b> {saved_job.job.location}", normal)
        )

        job_elements.append(
            Paragraph(f"<b>Source:</b> {saved_job.job.source}", normal)
        )

        job_elements.append(
            Paragraph(f"<b>Status:</b> {saved_job.status.value}", normal)
        )

        job_elements.append(
            Paragraph(f'<b>Link:</b> <a href= "{saved_job.job.link}">Open Job Posting</a>', normal)
        )

        if saved_job.notes:
            job_elements.append(
                Paragraph(
                    f"<b>Notes:</b> {saved_job.notes}",
                    normal,
                )
            )

        job_elements.append(Spacer(1, 15))
        elements.append(KeepTogether(job_elements))

    doc.build(elements)

    buffer.seek(0)

    return buffer


def generate_csv(saved_jobs):

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Title","Company","Location","Source","Status","Link","Notes"])
    for saved_job in saved_jobs:
        writer.writerow([
            saved_job.job.title,
            saved_job.job.company,
            saved_job.job.location,
            saved_job.job.source,
            saved_job.status,
            saved_job.job.link,
            saved_job.notes,
        ])

    buffer.seek(0)
    
    return buffer