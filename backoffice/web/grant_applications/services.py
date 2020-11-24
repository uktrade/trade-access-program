import io

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from web.grant_applications.models import GrantApplication


class GrantApplicationPdf:

    def __init__(self, grant_application: GrantApplication):
        self.header_footer_style = ParagraphStyle(
            'header_footer', fontName='Helvetica', fontSize=10, leading=16
        )
        self.page_number_style = ParagraphStyle(
            'header_footer', fontName='Helvetica', alignment=TA_RIGHT, fontSize=10, leading=16
        )
        self.heading_style = ParagraphStyle(
            'heading', fontName='Helvetica-Bold', fontSize=14, leading=18
        )
        self.question_style = ParagraphStyle(
            'question', fontName='Helvetica-Bold', fontSize=12, leading=16
        )
        self.answer_style = ParagraphStyle(
            'answer', fontName='Helvetica', fontSize=12, leading=16
        )

        self.a4_width, self.a4_height = A4
        self.left_margin = 0.75 * inch
        self.right_margin = self.a4_width - (0.5 * inch)
        self.indent = 0.3 * inch
        self.top_margin = self.a4_height - inch
        self.bottom_margin = inch
        self.header_margin = self.a4_height - (0.1 * inch)
        self.footer_margin = (0.1 * inch)
        self.large_y_space = 0.3 * inch
        self.small_y_space = 0.1 * inch
        self.writable_width = self.right_margin - self.left_margin

        self.y_position = self.top_margin

        # Create a file-like buffer to receive PDF data.
        self.buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file"
        self.pdf = canvas.Canvas(self.buffer)

        self.grant_application = grant_application

    def _start_new_page(self, height=0):
        self.pdf.showPage()
        self._draw_header()
        self._draw_footer()
        self.y_position = self.top_margin - height

    def _draw_header(self):
        details = Paragraph(
            '<br />\n'.join([
                f'Grant application ID: {self.grant_application.id}',
                f'Business name: {self.grant_application.company_name}',
                f'Date submitted: {self.grant_application.grant_management_process.created.date()}',
            ]),
            style=self.header_footer_style
        )
        w, h = details.wrap(self.writable_width, None)
        details.drawOn(self.pdf, self.left_margin, self.header_margin - h)

    def _draw_footer(self):
        details = Paragraph(
            f'Grant application ID: {self.grant_application.id}',
            style=self.header_footer_style
        )
        details.wrap(self.writable_width, None)
        details.drawOn(self.pdf, self.left_margin, self.footer_margin)

        page_number = Paragraph(
            f'page {self.pdf.getPageNumber()}',
            style=self.page_number_style
        )
        pw, ph = page_number.wrap(self.writable_width, None)
        page_number.drawOn(self.pdf, self.right_margin - pw, self.footer_margin)

    def _draw_heading(self, heading):
        heading = Paragraph(heading, style=self.heading_style)
        w, h = heading.wrap(self.writable_width, None)
        self.y_position -= + h

        if self.y_position < self.bottom_margin:
            self._start_new_page(height=h)

        heading.drawOn(self.pdf, self.left_margin, self.y_position)

    def _draw_row(self, question, answer):
        question_p = Paragraph(
            question,
            style=self.question_style
        )
        answer_p = Paragraph(
            str(answer).replace('\n', '<br />\n'),
            style=self.answer_style
        )
        table = Table(
            data=[[question_p, answer_p]],
            colWidths=[self.writable_width / 3, self.writable_width * 2 / 3],
            style=TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.lightgrey),
            ])
        )
        tw, th = table.wrap(0, 0)

        self.y_position -= + th

        if self.y_position < self.bottom_margin:
            self._start_new_page(height=th)

        table.drawOn(self.pdf, self.left_margin, self.y_position)

    def generate(self):
        self._draw_header()
        self._draw_footer()

        for i, section in enumerate(self.grant_application.application_summary):
            self.y_position -= self.large_y_space
            self._draw_heading(section['heading'])

            # Section questions/answers
            for row in section['rows']:
                self.y_position -= self.small_y_space
                self._draw_row(question=row['key'], answer=row['value'])

        # Close the PDF object cleanly
        self.pdf.showPage()
        self.pdf.save()

        self.buffer.seek(0)
        return self.buffer
