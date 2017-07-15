import requests
from django.conf import settings
import datetime
import string
import random
import os
from shutil import copyfile
from subprocess import call
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


def pdf_response(pdf_file, file_name):
    with open(pdf_file, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename={}'.format(file_name)
        response['pdf_file'] = pdf_file
        return response


def convert_html_to_pdf(html, pdf_file):
    html_file = '/tmp/{}.html'.format(str(uuid4()))
    with open(html_file, 'w') as f:
        f.write(html)
    cmd = settings.WKHTMLTOPDF_CMD
    cmd_options = settings.WKHTMLTOPDF_CMD_OPTIONS
    res = call([cmd] + cmd_options + [html_file, pdf_file])
    # res = res and call(['pdftk', pdf_file, 'output', pdf_file])
    # copyfile(html_file, 'render.html')
    os.remove(html_file)
    return res


def add_page_numbers_to_pdf(pdf_file, task_name):
    cmd = ('cpdf -add-text "{0} (%Page of %EndPage)" -font "Arial" ' + \
          '-font-size 10 -bottomright .75in {1} -o {1}').format(task_name.capitalize(), pdf_file)
    os.system(cmd)
