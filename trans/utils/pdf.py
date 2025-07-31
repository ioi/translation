import asyncio
import cairo
from datetime import datetime
import logging
import os
from pathlib import Path
from pikepdf import Pdf, Rectangle, AttachedFileSpec
from pikepdf.models.metadata import encode_pdf_date
from tempfile import TemporaryDirectory
from uuid import uuid4

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

    if task_type == 'released':
        markdown = translation.get_published_text()
    else:
        markdown = translation.get_latest_text()

    html = _render_pdf_template(
        translation, markdown,
        static_path=settings.STATIC_ROOT,
        images_path=settings.MEDIA_ROOT + '/images/',
        pdf_output=True,
    )

    with TemporaryDirectory(dir=_temp_dir_path()) as temp_dir:
        temp_dir_path = Path(temp_dir)
        loop = asyncio.get_event_loop()
        browser_pdf_path = loop.run_until_complete(_convert_html_to_pdf(html, temp_dir_path))
        transformed_pdf_path = temp_dir_path / 'transformed.pdf'
        if settings.USE_CPDF:
            _add_page_numbers_to_pdf(browser_pdf_path, transformed_pdf_path, task.name)
        else:
            _add_footer_to_pdf(browser_pdf_path, transformed_pdf_path, temp_dir_path,
                               '{task} ({page} of {num_pages})',
                               task=task.name, align_right=False)
        if settings.EMBED_MARKDOWN:
            embedding_pdf_path = temp_dir_path / 'embedding.pdf'
            _add_markdown_to_pdf(transformed_pdf_path, embedding_pdf_path, markdown)
            transformed_pdf_path = embedding_pdf_path
        transformed_pdf_path.rename(pdf_file_path)

    return str(pdf_file_path)


def build_final_pdf(translation: Translation) -> str:
    task_type = 'released' if translation.user.username == 'ISC' else 'task'
    return build_pdf(translation, task_type)


def build_printed_draft_pdf(contest_slug: str, pdf_file_path: str, info: str) -> str:
    draft_dir_path = Path(f'{settings.MEDIA_ROOT}/draft/{contest_slug}')
    draft_dir_path.mkdir(parents=True, exist_ok=True)
    output_pdf_path = draft_dir_path / (str(uuid4()) + '.pdf')
    if settings.USE_CPDF:
        _add_info_line_to_pdf(Path(pdf_file_path), output_pdf_path, info)
    else:
        _add_footer_to_pdf(Path(pdf_file_path), output_pdf_path, _temp_dir_path(), info, align_right=True)
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


def _render_pdf_template(translation: Translation, markdown: str,
                         static_path: str, images_path: str, pdf_output: bool) -> str:
    requested_user = translation.user
    task = translation.task

    context = {
        'content': markdown,
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


def _add_footer_to_pdf(src_pdf_path: Path, dst_pdf_path: Path, temp_dir_path: Path, footer: str, align_right: bool, **kwargs):
    with Pdf.open(src_pdf_path) as pdf:
        num_pages = len(pdf.pages)
        overlay_path = temp_dir_path / 'overlay.pdf'

        with cairo.PDFSurface(str(overlay_path), PAGE_WIDTH_POINTS, PAGE_HEIGHT_POINTS) as surface:
            ctx = cairo.Context(surface)

            for page in range(num_pages):
                ctx.select_font_face(SERIF_FONT)
                ctx.set_font_size(10)
                ctx.set_source_rgb(0.4, 0.4, 0.4)

                text = footer.format(page=page+1, num_pages=num_pages, **kwargs)
                textents = ctx.text_extents(text)
                fextents = ctx.font_extents()
                y = PAGE_HEIGHT_POINTS - 15 * POINTS_PER_MM
                y += fextents[0]
                margin = 10 * POINTS_PER_MM
                if align_right:
                    x = PAGE_WIDTH_POINTS - margin - textents.width
                else:
                    x = margin
                x -= textents.x_bearing
                ctx.move_to(x, y)
                ctx.show_text(text)

                ctx.show_page()

        with Pdf.open(overlay_path) as overlay_pdf:
            for page in range(num_pages):
                pdf.pages[page].add_overlay(overlay_pdf.pages[page], Rectangle(0, 0, PAGE_WIDTH_POINTS, PAGE_HEIGHT_POINTS))

        pdf.save(dst_pdf_path)


def _add_markdown_to_pdf(src_pdf_path: Path, dst_pdf_path: Path, markdown: str):
    with Pdf.open(src_pdf_path) as pdf:
        now = encode_pdf_date(datetime.now().astimezone())
        # XXX: Declaration of AttachedFileSpec is wrong, it has an extra positional argument
        afs = AttachedFileSpec(pdf,
                               markdown.encode('utf-8'),
                               description='Task statement in Markdown',
                               filename='task.md',
                               mime_type='text/markdown; charset=UTF-8',
                               creation_date=now,
                               mod_date=now)
        pdf.attachments['markdown'] = afs

        pdf.save(dst_pdf_path)
