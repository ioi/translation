import asyncio
import os
from uuid import uuid4
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string

from pyppeteer import launch

from trans.context_processors import ioi_settings
from trans.models import Translation, User

logger = logging.getLogger(__name__)

POINTS_PER_MM = 72 / 25.4

# Default is A4 paper
PAGE_WIDTH_POINTS = getattr(settings, 'PAGE_WIDTH_MM', 210) * POINTS_PER_MM
PAGE_HEIGHT_POINTS = getattr(settings, 'PAGE_HEIGHT_MM', 297) * POINTS_PER_MM

SERIF_FONT = 'Times New Roman'
SANS_FONT = 'Arial'


def build_pdf(translation: Translation, task_type: str) -> str:
    # task_type is either "released" for the ISC version, or "task" for a translation
    task = translation.task
    user = translation.user
    pdf_file_path = _cached_pdf_path(task.contest.slug, task.name, task_type, user)

    last_edit_time = translation.get_latest_change_time()
    assert last_edit_time is not None
    rebuild_needed = not pdf_file_path.exists() or pdf_file_path.stat().st_mtime < last_edit_time
    if not rebuild_needed:
        return str(pdf_file_path)

    html = _render_pdf_template(
        translation, task_type,
        static_path=settings.STATIC_ROOT,
        images_path=settings.MEDIA_ROOT + '/images/',
        pdf_output=True,
    )

    with TemporaryDirectory(dir=_temp_dir_path()) as temp_dir:
        temp_dir_path = Path(temp_dir)
        loop = asyncio.get_event_loop()
        browser_pdf_path = loop.run_until_complete(_convert_html_to_pdf(html, temp_dir_path))
        transformed_pdf_path = temp_dir_path / 'transformed.pdf'
        _add_page_numbers_to_pdf(browser_pdf_path, transformed_pdf_path, task.name)
        transformed_pdf_path.rename(pdf_file_path)

    return str(pdf_file_path)


def build_final_pdf(translation: Translation) -> str:
    task_type = 'released' if translation.user.username == 'ISC' else 'task'
    return build_pdf(translation, task_type)


def build_printed_draft_pdf(contest_slug: str, pdf_file_path: str, info: str) -> str:
    draft_dir_path = Path(f'{settings.MEDIA_ROOT}/draft/{contest_slug}')
    draft_dir_path.mkdir(parents=True, exist_ok=True)
    output_pdf_path = draft_dir_path / (str(uuid4()) + '.pdf')
    _add_info_line_to_pdf(Path(pdf_file_path), output_pdf_path, info)
    return str(output_pdf_path)


def remove_cached_pdfs(user: User) -> None:
    """Remove all cached generated PDF for a given user."""
    for trans in Translation.objects.filter(user=user):
        for task_type in ['released', 'task']:
            pdf_path = _cached_pdf_path(trans.task.contest.slug, trans.task.name, task_type, user)
            pdf_path.unlink(missing_ok=True)


def get_file_name_from_path(file_path: str) -> str:
    return file_path.split('/')[-1]


def pdf_response(pdf_file_path: str, file_name: str) -> HttpResponse:
    with open(pdf_file_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename={}'.format(file_name)
        response['pdf_file_path'] = pdf_file_path
        return response


def _render_pdf_template(translation: Translation, task_type: str,
                         static_path: str, images_path: str, pdf_output: bool) -> str:
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


def _cached_pdf_path(contest_slug: str, task_name: str, task_type: str, user: User) -> Path:
    dir_path = Path(f'{settings.CACHE_DIR}/{contest_slug}/{task_name}/{task_type}')
    dir_path.mkdir(parents=True, exist_ok=True)
    pdf_path = dir_path / f'{task_name}-{user.username}.pdf'
    return pdf_path


def _temp_dir_path() -> Path:
    temp_path = Path(f'{settings.CACHE_DIR}/tmp')
    os.makedirs(temp_path, exist_ok=True)
    return temp_path


async def _convert_html_to_pdf(html: str, temp_dir_path: Path) -> Path:
    html_file = temp_dir_path / 'source.html'
    pdf_file = temp_dir_path / 'browser.pdf'

    try:
        with open(html_file, 'w') as f:
            f.write(html)
        browser = await launch(options={'args': ['--no-sandbox']})
        page = await browser.newPage()
        await page.goto('file://{}'.format(html_file), {
            'waitUntil': 'networkidle2',
        })
        await page.emulateMedia('print')
        await page.pdf({'path': str(pdf_file), **settings.PYPPETEER_PDF_OPTIONS})
        await browser.close()
    except Exception as e:
        logger.error(e)

    return pdf_file


def _add_page_numbers_to_pdf(src_pdf_path: Path, dst_pdf_path: Path, task_name: str) -> None:
    color =  '-color "0.4 0.4 0.4" '
    cmd = ('cpdf -add-text "{0} (%Page of %EndPage)   " -font "Arial" ' + color + \
          '-font-size 10 -bottomright .62in {1} -o {2}').format(task_name, src_pdf_path, dst_pdf_path)
    os.system(cmd)


def _add_info_line_to_pdf(src_pdf_path: Path, dst_pdf_path: Path, info: str) -> None:
    color =  '-color "0.4 0.4 0.4" '
    cmd = 'cpdf -add-text "   {}" -font "Arial" -font-size 10 -bottomleft .62in {} -o {} {}'.format(
        info, src_pdf_path, dst_pdf_path, color)
    os.system(cmd)
