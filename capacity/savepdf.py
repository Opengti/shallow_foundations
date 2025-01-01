from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Function to add page numbers
from reportlab.lib.units import mm
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io
import os



# Function to get table style
def get_table_style():
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ])


def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    text = f"Page {page_num+1}"
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(200 * mm, 15 * mm, text)


def compile_content_page(series0, series1, series2, series3, dataframe4, titlelist, capacity):
    df_list =[series0.reset_index(), series1.reset_index(), series2.reset_index(), series3.reset_index(), dataframe4.reset_index()]
    df_list[0].columns = ['Dimensions', 'Values']
    df_list[1].columns = ['Soil Parameters', 'Values']
    df_list[2].columns = ['Geometry', 'Values']
    df_list[3].columns = ['Loads', 'Values']
    df_list[4].columns = ['Factors', 'Nc', 'Ng', 'Nq']


    # Prepare data for each table
    datalist = [None]*5
    for i in range(5):
        datalist[i] = [df_list[i].columns.tolist()] + df_list[i].values.tolist()


    # Define page size and margins
    PAGE_WIDTH, PAGE_HEIGHT = A4
    LEFT_MARGIN = RIGHT_MARGIN = 30
    TOP_MARGIN = BOTTOM_MARGIN = 30

    # Calculate available width
    available_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

    # Define column widths for child tables (e.g., two tables side by side)
    child_table_width = (available_width - inch) / 2  # Subtracting 1 inch for spacing

    # Create Table 1 to Table 4
    tablelist = [None]*5
    for i in range(5):
        tablelist[i] = Table(datalist[i], colWidths=[child_table_width * 0.6, child_table_width * 0.4])
        tablelist[i].setStyle(get_table_style())



    # Create a parent table with two columns and a spacer
    table_row_a = Table([
        [tablelist[0], Spacer(1, 0), tablelist[1]]
    ], colWidths=[child_table_width, 20, child_table_width])  # 20 points spacer

    table_row_b = Table([
        [tablelist[2], Spacer(1, 0), tablelist[3]]
    ], colWidths=[child_table_width, 20, child_table_width])  # 20 points spacer

    # Parent table style
    table_row_a.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align tables to the top
    ]))

    table_row_b.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align tables to the top
    ]))

    # Initialize PDF document
    pdf = SimpleDocTemplate(
        "reports/content_page.pdf",
        pagesize=A4,
        rightMargin=RIGHT_MARGIN,
        leftMargin=LEFT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="Calculation Report",
        author="OpenGTi",
        compress=True
    )

    # Initialize styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']

    # Create title and subtitle
    title = Paragraph("Ultimate Bearing Capacity", subtitle_style)
    project_name = Paragraph(f"Project Name: {titlelist[0]}", normal_style)
    project_ID = Paragraph(f"Project No.: {titlelist[1]}", normal_style)
    structure_ID = Paragraph(f"Structure ID: {titlelist[2]}", normal_style)
    inputparameters = Paragraph("Input parameters:", normal_style)
    outputs = Paragraph("Calculation Results:", normal_style)
    result = Paragraph(capacity, normal_style)

    # Create spacing
    spacer = Spacer(1, 12)

    # Assemble elements
    elements = [
        title,
        project_name,
        project_ID,
        structure_ID,
        spacer,
        inputparameters,
        table_row_a,
        spacer,
        table_row_b,
        spacer,
        tablelist[4],
        spacer,
        outputs,
        result
    ]

    pdf.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

def combine_pdf(text, file1, file2):
    # Ensure the "reports" folder exists
    if not os.path.exists("reports"):
        os.makedirs("reports")

    # Build output file path (final combined PDF)
    output_path = os.path.join("reports", f"{text}.pdf")

    # Load the two PDF files
    reader1 = PdfReader(file1 + ".pdf")
    reader2 = PdfReader(file2 + ".pdf")

    # Create a writer object to combine pages
    writer = PdfWriter()

    # Add the first page of file1.pdf
    writer.add_page(reader1.pages[0])

    # Add the first page of file2.pdf
    writer.add_page(reader2.pages[0])

    # Write to the new file in the "reports" folder
    with open(output_path, "wb") as output_pdf:
        writer.write(output_pdf)
    print(f"PDF file saved as {output_path}")

    # ---------------------------------------
    # Remove temporary PDFs after combining
    # ---------------------------------------
    try:
        os.remove(file1 + ".pdf")
        os.remove(file2 + ".pdf")
        print("Temporary files removed.")
    except OSError as e:
        print(f"Error removing temp files: {e}")


def generate_dynamic_content(list):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    c.setFont("Helvetica", 10)

    row = 720

    # Add dynamic content based on data
    c.drawString(94, row, f"Project Name: {list[0]}")
    c.drawString(94, row-15, f"Project No.: {list[1]}")
    c.drawString(94, row-30, f"Structure ID: {list[2]}")
    c.drawString(94, row-45, f"Other text1:")
    c.drawString(94, row-60, f"Other text2:")

    # Add more dynamic elements as needed
    # For example, tables, charts, etc.

    c.save()
    packet.seek(0)
    return packet


def merge_pdfs(template_file, dynamic_pdf, output_file):
    # Read the template PDF
    template_pdf = PdfReader(template_file)
    # Read the dynamic content PDF
    dynamic_pdf_reader = PdfReader(dynamic_pdf)
    dynamic_page = dynamic_pdf_reader.pages[0]

    writer = PdfWriter()

    # Assume template has at least one page
    for page_num in range(len(template_pdf.pages)):
        template_page = template_pdf.pages[page_num]
        if page_num == 0:
            # Merge dynamic content onto the first page
            template_page.merge_page(dynamic_page)
        writer.add_page(template_page)

    # Write out the merged PDF
    with open(output_file, "wb") as f:
        writer.write(f)


def prepare_frontpage(list):
    # prepare output file as temp_frontpage.pdf

    template_file = "templates/report_template.pdf"
    output_file = "reports/temp_frontpage.pdf"


    # Step 2: Generate dynamic content PDF
    dynamic_pdf = generate_dynamic_content(list)

    # Step 3: Merge the template and dynamic content
    merge_pdfs(template_file, dynamic_pdf, output_file)






