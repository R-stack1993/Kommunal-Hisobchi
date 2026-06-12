# pdf_report.py
import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from locales import get_text


def generate_monthly_pdf(
    house_name: str,
    utility_type: str,
    month_year: str,
    start_reading: float,
    end_reading: float,
    usage: float,
    cost: float,
    date_generated: str,
    lang: str = 'uz'
) -> io.BytesIO:
    """
    Generate a monthly PDF report and return it as a BytesIO buffer.

    Parameters:
        house_name: Name of the house/address
        utility_type: 'elektr' or 'gaz'
        month_year: Month and year string (e.g., "01/2025")
        start_reading: Start reading value for the month
        end_reading: End reading value for the month
        usage: Total usage for the month
        cost: Total cost for the month
        date_generated: Date the report was generated
        lang: Language code ('uz' or 'ru')

    Returns:
        BytesIO buffer containing the PDF document
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1  # Center
    )
    normal_style = styles['Normal']

    elements = []

    # Title
    title_text = get_text('pdf_title', lang)
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 12))

    # Utility display name
    icon = "Elektr" if utility_type == "elektr" else "Gaz"
    utility_display = get_text('pdf_utility_elektr', lang) if utility_type == "elektr" else get_text('pdf_utility_gaz', lang)

    # Table data
    table_data = [
        [get_text('pdf_col_house', lang), house_name],
        [get_text('pdf_col_utility', lang), utility_display],
        [get_text('pdf_col_month', lang), month_year],
        [get_text('pdf_col_start_reading', lang), f"{start_reading:,.0f}"],
        [get_text('pdf_col_end_reading', lang), f"{end_reading:,.0f}"],
        [get_text('pdf_col_usage', lang), f"{usage:,.0f}"],
        [get_text('pdf_col_cost', lang), f"{cost:,.0f}"],
        [get_text('pdf_col_date', lang), date_generated],
    ]

    table = Table(table_data, colWidths=[7 * cm, 9 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.9, 0.9, 0.95)),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.white, colors.Color(0.97, 0.97, 1.0)]),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Footer note
    footer_text = get_text('pdf_footer', lang)
    elements.append(Paragraph(footer_text, normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
