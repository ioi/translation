import os
from uuid import uuid4
import logging

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string

import pdfkit
from xvfbwrapper import Xvfb

logger = logging.getLogger(__name__)

from trans.utils.translation import get_requested_user, \
    get_task_by_contest_and_name, get_trans_by_user_and_task


def render_pdf_template(request, user, contest_slug, task_name, task_type,
                        static_path, images_path, pdf_output):
    requested_user = get_requested_user(request, task_type)
    task = get_task_by_contest_and_name(contest_slug, task_name,
                                        user.is_editor())

    if task_type == 'released':
        content = task.get_published_text()
    else:
        trans = get_trans_by_user_and_task(requested_user, task)
        content = trans.get_latest_text()

    context = {
        'content': content,
        'contest': task.contest.title,
        'task_name': task.name,
        'country': requested_user.country.code,
        'language': requested_user.language.name,
        'language_code': requested_user.language.code,
        'direction': requested_user.language.direction(),
        'username': requested_user.username,
        'pdf_output': pdf_output,
        'static_path': static_path,
        'images_path': images_path,
        'text_font_base64': requested_user.text_font_base64
    }
    return render_to_string('pdf-template.html', context=context,
                            request=request)


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
    try:
        html_file_path = '/tmp/{}.html'.format(str(uuid4()))
        with open(html_file_path, 'wb') as f:
            f.write(html.encode('utf-8'))
        with Xvfb():
            pdfkit.from_file(html_file_path, pdf_file_path, options=settings.WKHTMLTOPDF_CMD_OPTIONS)
        os.remove(html_file_path)
    except Exception as e:
        logger.error(e)


def add_page_numbers_to_pdf(pdf_file_path, task_name):
    cmd = ('cpdf -add-text "{0} (%Page of %EndPage)" -font "Arial" ' +
          '-font-size 10 -bottomright .75in {1} -o {1}').format(task_name.capitalize(), pdf_file_path)
    os.system(cmd)


def add_info_line_to_pdf(pdf_file_path, info):
    output_pdf_path = '/tmp/{}.pdf'.format(str(uuid4()))
    cmd = 'cpdf -add-text "{}" -font "Arial" -font-size 10 -bottomleft .75in {} -o {}'.format(
        info, pdf_file_path, output_pdf_path)
    os.system(cmd)
    return output_pdf_path
