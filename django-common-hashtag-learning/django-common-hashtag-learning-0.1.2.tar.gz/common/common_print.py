from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.tables import TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch

from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors

from reportlab.rl_config import defaultPageSize

from django.http import HttpResponse

import io




class PrintDocument:

    def __init__(self, footer, document_type):

        self.front_page_header_1 = ParagraphStyle(name="fp_header_1", alignment=TA_CENTER, fontName="Helvetica", fontSize=32, leading=32)
        self.front_page_header_2 = ParagraphStyle(name="fp_header_2", alignment=TA_CENTER, fontName="Helvetica", fontSize=22, leading=22)
        self.front_page_header_2_left = ParagraphStyle(name="fp_header_2_l", alignment=TA_LEFT, fontName="Helvetica",fontSize=22, leading=22)

        self.front_page_header_3 = ParagraphStyle(name="fp_header_3", fontName="Helvetica", fontSize=14, )
        self.front_page_header_3_left = ParagraphStyle(name="fp_header_3_l", alignment=TA_LEFT, fontName="Helvetica", fontSize=14, )
        self.front_page_header_4 = ParagraphStyle(name="fp_header_4", alignment=TA_CENTER, fontName="Helvetica", fontSize=16, )
        self.front_page_header_4_left = ParagraphStyle(name="fp_header_4_1", alignment=TA_LEFT, fontName="Helvetica", fontSize=16, )

        self.page_normal = ParagraphStyle(name='page_normal', fontName='Helvetica', fontSize=11, spaceAfter=12)
        self.page_bold = ParagraphStyle(name='page_bold', fontName='Helvetica-Bold', fontSize=11, spaceAfter=12)
        self.page_italic = ParagraphStyle(name='page_italic', fontName='Helvetica-Oblique', fontSize=11, spaceAfter=12)

        self.page_normal_half_space = ParagraphStyle(name='page_normal_half_space', fontName='Helvetica', fontSize=11, spaceAfter=6)

        self.table_page_normal = ParagraphStyle(name='table_page_normal', fontName='Helvetica', fontSize=11)
        self.table_page_bold = ParagraphStyle(name='table_page_bold', fontName='Helvetica-Bold', fontSize=11)

        self.footer = footer
        self.document_type = document_type

        self.regular_table = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LINEABOVE', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.black),
            ('LINEAFTER', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ])




    def create_doc(self, story, first_page_footer, doc_name, landscape_mode):
        self.landscape_mode = landscape_mode
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = doc_name

        buf = io.BytesIO()

        # Setup the document with paper size and margins
        if landscape_mode is True:
            pagesize = (defaultPageSize[1], defaultPageSize[0])
        else:
            pagesize = (defaultPageSize[0], defaultPageSize[1])

        doc = SimpleDocTemplate(
            buf,
            pagesize=pagesize,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
        )


        if first_page_footer is True:
            if landscape_mode is False:
                doc.build(story,
                          onFirstPage=self.add_hashtag_footer,
                          onLaterPages=self.add_hashtag_footer)
            else:
                doc.build(story,
                          onFirstPage=self.landscape_page,
                          onLaterPages=self.landscape_page)

        else:
            doc.build(story,
                      onLaterPages=self.add_hashtag_footer)

        pdf = buf.getvalue()
        buf.close()
        response.write(pdf)

        return response


    def add_hashtag_footer(self, canvas, doc):

        if self.landscape_mode is True:
            page_width = defaultPageSize[1]
        else:
            page_width = defaultPageSize[0]

        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        page_number_text = "%d" % (doc.page)


        canvas.drawCentredString(
            page_width / 2.0,
            0.4 * inch,
            page_number_text
        )

        # divide by 256 because the rgb values are 0 to 1
        canvas.setFillColorRGB(100 / 256, 100 / 256, 100 / 256)
        canvas.drawRightString(
            page_width - inch,
            0.4 * inch,
            'Hashtag Learning: Impact'
        )

        if (self.document_type == 'Improvement Plan' or self.document_type == 'Evidence' or
            self.document_type == 'QI Report' or self.document_type == 'Comments'):
            canvas.drawString(
                inch,
                0.4 * inch,
                self.footer
            )


        canvas.restoreState()

    def landscape_page(self, canvas, doc):
        canvas.setPageSize(landscape(A4))
        self.add_hashtag_footer(canvas, doc)