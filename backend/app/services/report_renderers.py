import csv
import io
from datetime import datetime

from app.services.report_data_builder import ReportData


def render_pdf(data: ReportData) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(data.title, styles["Title"]),
        Paragraph(data.subtitle, styles["Normal"]),
        Paragraph(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} by AuditOS", styles["Normal"]),
        Spacer(1, 0.25 * inch),
    ]

    if data.kpis:
        kpi_table = Table([[k, v] for k, v in data.kpis], colWidths=[3 * inch, 3 * inch])
        kpi_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ]
            )
        )
        elements += [kpi_table, Spacer(1, 0.35 * inch)]

    if data.table_rows:
        table_data = [data.table_headers] + data.table_rows
        main_table = Table(table_data, repeatRows=1)
        main_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(main_table)
    else:
        elements.append(Paragraph("No data available for this period.", styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()


def render_excel(data: ReportData) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.title = data.title[:31]

    ws.append([data.title])
    ws["A1"].font = Font(size=16, bold=True)
    ws.append([data.subtitle])
    ws.append([])

    if data.kpis:
        for label, value in data.kpis:
            ws.append([label, value])
            ws.cell(ws.max_row, 1).font = Font(bold=True)
        ws.append([])

    if data.table_headers:
        header_row = ws.max_row + 1
        ws.append(data.table_headers)
        header_fill = PatternFill(start_color="1D4ED8", end_color="1D4ED8", fill_type="solid")
        for cell in ws[header_row]:
            cell.font = Font(color="FFFFFF", bold=True)
            cell.fill = header_fill
        for row in data.table_rows:
            ws.append(row)

    for column_cells in ws.columns:
        length = max((len(str(c.value)) for c in column_cells if c.value is not None), default=10)
        ws.column_dimensions[column_cells[0].column_letter].width = min(max(length + 2, 12), 50)

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def render_csv(data: ReportData) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([data.title])
    writer.writerow([data.subtitle])
    writer.writerow([])
    for label, value in data.kpis:
        writer.writerow([label, value])
    writer.writerow([])
    if data.table_headers:
        writer.writerow(data.table_headers)
        writer.writerows(data.table_rows)
    return buffer.getvalue().encode("utf-8")
