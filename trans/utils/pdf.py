import asyncio
import os
from urllib.parse import urljoin
from uuid import uuid4
import logging
import requests

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string

from shutil import copyfile
from pyppeteer import launch

from trans.context_processors import ioi_settings

logger = logging.getLogger(__name__)

def render_pdf_template(translation, task_type,
                        static_path, images_path, pdf_output):
    requested_user = translation.user
    task = translation.task

    if task_type == 'released':
        content = translation.get_published_text()
    else:
        content = translation.get_latest_text()

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
    context.update(ioi_settings(None))
    return render_to_string('pdf-template.html', context=context)

# pdf file paths (excepting final pdf path)
def output_pdf_path(contest_slug, task_name, task_type, user):
    file_path = '{}/output/{}/{}/{}'.format('/tmp/ioi-translation', contest_slug, task_name, task_type)
    file_name = '{}-{}.pdf'.format(task_name, user.username)
    pdf_file_path = '{}/{}'.format(file_path, file_name)
    os.makedirs(file_path, exist_ok=True)
    return pdf_file_path

def released_pdf_path(contest_slug, task_name, user):
    return output_pdf_path(contest_slug, task_name, 'released', user)

def unreleased_pdf_path(contest_slug, task_name, user):
    return output_pdf_path(contest_slug, task_name, 'task', user)

# base pdf is a pdf of ISC
def base_pdf_path(contest_slug, task_name, task_type):
    user = User.objects.get(username='ISC')
    return output_pdf_path(contest_slug, task_name, task_type, user)

def build_pdf(translation, task_type):
    task = translation.task
    user = translation.user
    pdf_file_path = output_pdf_path(task.contest.slug, task.name, task_type, user)

    last_edit_time = translation.get_latest_change_time()
    rebuild_needed = not os.path.exists(pdf_file_path) or os.path.getmtime(pdf_file_path) < last_edit_time
    if not rebuild_needed:
        return pdf_file_path

    html = render_pdf_template(
        translation, task_type,
        static_path=settings.STATIC_ROOT,
        images_path=settings.MEDIA_ROOT + 'images/',
        pdf_output=True,
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(convert_html_to_pdf(html, pdf_file_path))
    add_page_numbers_to_pdf(pdf_file_path, task.name)
    return pdf_file_path


def build_final_pdf(translation):
    task_type = 'released' if translation.user.username == 'ISC' else 'task'
    return build_pdf(translation, task_type)


def get_file_name_from_path(file_path):
    return file_path.split('/')[-1]


def pdf_response(pdf_file_path, file_name):
    with open(pdf_file_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename={}'.format(file_name)
        response['pdf_file_path'] = pdf_file_path
        return response


async def convert_html_to_pdf(html, pdf_file_path):
    try:
        html_file_path = '/tmp/{}.html'.format(str(uuid4()))
        with open(html_file_path, 'wb') as f:
            f.write(html.encode('utf-8'))
        browser = await launch(options={'args': ['--no-sandbox']})
        page = await browser.newPage()
        await page.goto('file://{}'.format(html_file_path), {
            'waitUntil': 'networkidle2',
        })
        await page.emulateMedia('print')
        await page.pdf({'path': pdf_file_path, **settings.PYPPETEER_PDF_OPTIONS})
        await browser.close()
        os.remove(html_file_path)
    except Exception as e:
        logger.error(e)


def add_page_numbers_to_pdf(pdf_file_path, task_name):
    color =  '-color "0.4 0.4 0.4" '
    cmd = ('cpdf -add-text "{0} (%Page of %EndPage)   " -font "Arial" ' + color + \
          '-font-size 10 -bottomright .62in {1} -o {1}').format(task_name, pdf_file_path)
    os.system(cmd)


def build_printed_draft_pdf(contest_slug, pdf_file_path, info):
    os.system('mkdir -p media/draft/{}'.format(contest_slug))
    output_pdf_path = 'media/draft/{}/{}.pdf'.format(contest_slug, str(uuid4()))
    _add_info_line_to_pdf(output_pdf_path, pdf_file_path, info)
    return output_pdf_path


def merge_final_pdfs(task_names, contest_slug, language_code):
    os.system('mkdir -p media/merged/{}'.format(contest_slug)) # create dir silently if doeesnt exist
    output_pdf_path = 'media/merged/{}/{}-merged.pdf'.format(contest_slug, language_code)

    cmd = 'cpdf '

    for task_name in task_names:
        cmd = cmd + 'media/final_pdf/{}/{}.pdf '.format(task_name, language_code)
    cmd = cmd + '-o {}'.format(output_pdf_path)

    os.system(cmd)
    return output_pdf_path


def _add_info_line_to_pdf(output_pdf_path, pdf_file_path, info):
    color =  '-color "0.4 0.4 0.4" '
    cmd = 'cpdf -add-text "   {}" -font "Arial" -font-size 10 -bottomleft .62in {} -o {} {}'.format(
        info, pdf_file_path, output_pdf_path, color)
    os.system(cmd)
