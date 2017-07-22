from django.conf import settings
import os
from uuid import uuid4

from django.http import HttpResponse, JsonResponse


def unreleased_pdf_path(pdf_name):
    if pdf_name.split('.')[-1] == 'pdf':
        return '%s%s' % (settings.MEDIA_ROOT, pdf_name)
    return '%s%s.pdf' % (settings.MEDIA_ROOT, pdf_name)


def final_pdf_path(pdf_name):
    if pdf_name.split('.')[-1] == 'pdf':
        return '%s/%s' % (settings.FINAL_PDF_ROOT, pdf_name)
    return '%s/%s.pdf' % (settings.FINAL_PDF_ROOT, pdf_name)


def pdf_response(pdf_file_path, file_name):
    with open(pdf_file_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename={}'.format(file_name)
        response['pdf_file_path'] = pdf_file_path
        return response


def convert_html_to_pdf(html, pdf_file_path):
    html_file_path = '/tmp/{}.html'.format(str(uuid4()))
    with open(html_file_path, 'w') as f:
        f.write(html)
    cmd = settings.WKHTMLTOPDF_CMD
    cmd_options = ['--{} {}'.format(a, b) for a, b in settings.WKHTMLTOPDF_CMD_OPTIONS.items()]
    cmd = '{} {} {} {}'.format(cmd, ' '.join(cmd_options), html_file_path, pdf_file_path)
    # print(cmd)
    os.system(cmd)
    os.remove(html_file_path)

    # fix corrupted pdf file
    cmd = 'pdftk {0} output {0}'.format(pdf_file_path)
    os.system(cmd)


def add_page_numbers_to_pdf(pdf_file_path, task_name):
    cmd = ('cpdf -add-text "{0} (%Page of %EndPage)" -font "Arial" ' + \
          '-font-size 10 -bottomright .75in {1} -o {1}').format(task_name.capitalize(), pdf_file_path)
    os.system(cmd)


def add_info_line_to_pdf(pdf_file_path, info):
    output_pdf_path = '/tmp/{}.pdf'.format(str(uuid4()))
    cmd = 'cpdf -add-text "{}" -font "Arial" -font-size 10 -bottomleft .75in {} -o {}'.format(
        info, pdf_file_path, output_pdf_path)
    os.system(cmd)
    return output_pdf_path
