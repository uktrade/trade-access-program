import io

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from web.grant_applications.models import GrantApplication


class GrantApplicationPdf:

    def __init__(self, grant_application: GrantApplication):
        self.title_style = ParagraphStyle(
            'title', fontName='Helvetica-Bold', fontSize=16, leading=20
        )
        self.details_style = ParagraphStyle(
            'details', fontName='Helvetica', fontSize=12, leading=16
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

        self.a4_width = 8.3 * inch
        self.a4_height = 11.7 * inch
        self.left_margin = 0.75 * inch
        self.right_margin = 0.5 * inch
        self.indent = 0.3 * inch
        self.first_top_position = 10.7 * inch
        self.top_margin = 11 * inch
        self.bottom_margin = 1.4 * inch
        self.large_y_space = 0.3 * inch
        self.small_y_space = 0.1 * inch
        self.wrap_width = self.a4_width - self.left_margin - self.right_margin

        self.y_position = self.first_top_position

        # Create a file-like buffer to receive PDF data.
        self.buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file"
        self.pdf = canvas.Canvas(self.buffer)

        self.grant_application = grant_application

    def _start_new_page(self, height=0):
        self.pdf.showPage()
        self.y_position = self.top_margin - height

    def _draw_title(self):
        title = Paragraph('TAP Grant Application', style=self.title_style)
        w, h = title.wrap(self.wrap_width, None)
        self.y_position -= h
        title.drawOn(self.pdf, self.left_margin, self.y_position)

    def _draw_details(self):
        # Application details
        details = Paragraph(
            '<br />\n'.join([
                f'Grant application ID: {self.grant_application.id}',
                f'Business name: {self.grant_application.company_name}',
                f'Date submitted: {self.grant_application.grant_management_process.created.date()}',
            ]),
            style=self.details_style
        )
        w, h = details.wrap(self.wrap_width, None)
        self.y_position -= h
        details.drawOn(self.pdf, self.left_margin, self.y_position)

    def _draw_heading(self, heading):
        heading = Paragraph(heading, style=self.heading_style)
        w, h = heading.wrap(self.wrap_width, None)
        self.y_position -= self.large_y_space + h

        if self.y_position < self.bottom_margin:
            self._start_new_page(height=h)

        heading.drawOn(self.pdf, self.left_margin, self.y_position)

    def _draw_question(self, question):
        question = Paragraph(question, style=self.question_style)
        w, h = question.wrap(self.wrap_width - self.indent, None)
        self.y_position -= self.small_y_space + h

        if self.y_position < self.bottom_margin:
            self._start_new_page(height=h)

        question.drawOn(self.pdf, self.left_margin + self.indent, self.y_position)

    def _draw_answer(self, answer):
        _answer = str(answer).replace('\n', '<br />\n')
        answer = Paragraph(_answer, style=self.answer_style)
        w, h = answer.wrap(self.wrap_width - self.indent, None)
        self.y_position -= self.small_y_space + h

        if self.y_position < self.bottom_margin:
            self._start_new_page(height=h)

        answer.drawOn(self.pdf, self.left_margin + self.indent, self.y_position)

    def generate(self):
        self._draw_title()
        self.y_position -= self.large_y_space
        self._draw_details()
        self.y_position -= self.large_y_space

        for section in self.grant_application.application_summary:
            self._draw_heading(section['heading'])

            # Section questions/answers
            for row in section['rows']:
                self._draw_question(row['key'])
                self._draw_answer(row['value'])

        # Close the PDF object cleanly
        self.pdf.showPage()
        self.pdf.save()

        self.buffer.seek(0)
        return self.buffer
