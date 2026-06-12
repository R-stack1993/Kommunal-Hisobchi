# pdf_report.py
import io
import os
import glob
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from locales import get_text


def _find_dejavu_font():
    """
    Search for DejaVuSans.ttf in common locations and return
    the path if found, otherwise return None.
    """
    search_paths = []

    # 1. Check reportlab's own fonts directory
    try:
        import reportlab
        reportlab_dir = os.path.dirname(reportlab.__file__)
        search_paths.append(os.path.join(reportlab_dir, 'fonts', 'DejaVuSans.ttf'))
        search_paths.append(os.path.join(reportlab_dir, 'fonts', 'DejaVu', 'DejaVuSans.ttf'))
    except ImportError:
        pass

    # 2. Check matplotlib's bundled fonts
    try:
        import matplotlib
        mpl_dir = os.path.dirname(matplotlib.__file__)
        search_paths.append(os.path.join(mpl_dir, 'mpl-data', 'fonts', 'ttf', 'DejaVuSans.ttf'))
    except ImportError:
        pass

    # 3. Common system font paths
    search_paths.extend([
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/DejaVuSans.ttf',
        '/usr/local/share/fonts/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf',
    ])

    # 4. Glob search in /usr/share/fonts/
    for pattern in glob.glob('/usr/share/fonts/**/DejaVuSans.ttf', recursive=True):
        search_paths.append(pattern)

    # 5. Check in Python's site-packages
    try:
        import site
        for site_dir in site.getsitepackages():
            search_paths.append(os.path.join(site_dir, 'reportlab', 'fonts', 'DejaVuSans.ttf'))
    except (ImportError, AttributeError):
        pass

    for path in search_paths:
        if os.path.isfile(path):
            return path

    return None


def _find_any_unicode_font():
    """
    Fallback: search for any TTF font that supports Unicode/Cyrillic.
    """
    fallback_fonts = [
        'FreeSans.ttf',
        'LiberationSans-Regular.ttf',
        'NotoSans-Regular.ttf',
        'Ubuntu-R.ttf',
        'Arial.ttf',
    ]
    font_dirs = [
        '/usr/share/fonts/',
        '/usr/local/share/fonts/',
    ]

    for font_dir in font_dirs:
        for font_name in fallback_fonts:
            for path in glob.glob(os.path.join(font_dir, '**', font_name), recursive=True):
                if os.path.isfile(path):
                    return path

    return None


def _register_unicode_font():
    """
    Register a Unicode-capable font (DejaVuSans preferred) with reportlab.
    Returns the font name to use in styles.
    """
    font_path = _find_dejavu_font()
    if font_path:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        return 'DejaVuSans'

    # Fallback to any Unicode font
    fallback_path = _find_any_unicode_font()
    if fallback_path:
        font_name = os.path.splitext(os.path.basename(fallback_path))[0]
        pdfmetrics.registerFont(TTFont(font_name, fallback_path))
        return font_name

    # Last resort: use Helvetica (will show tofu for Cyrillic but won't crash)
    return 'Helvetica'


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

    # Register Unicode font for Cyrillic/Uzbek support
    font_name = _register_unicode_font()

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=16,
        spaceAfter=20,
        alignment=1  # Center
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
    )

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
        ('FONTNAME', (0, 0), (0, -1), font_name),
        ('FONTNAME', (1, 0), (1, -1), font_name),
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
