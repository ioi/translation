import requests
from django.conf import settings


def unreleased_pdf_path(pdf_name):
    if pdf_name.split('.')[-1] == 'pdf':
        return '%s/%s' % (settings.MEDIA_ROOT, pdf_name)
    return '%s/%s.pdf' % (settings.MEDIA_ROOT, pdf_name)


def final_pdf_path(pdf_name):
    if pdf_name.split('.')[-1] == 'pdf':
        return '%s/%s' % (settings.FINAL_PDF_ROOT, pdf_name)
    return '%s/%s.pdf' % (settings.FINAL_PDF_ROOT, pdf_name)


def add_pdf_to_file(pdf_response):
    with open(unreleased_pdf_path(pdf_response.filename), 'wb') as file:
        file.write(pdf_response.content)


def send_pdf_to_printer_with_header_page(pdf_file_path, country_code, country_name, count=1):
    pdf_file = open(pdf_file_path, 'rb')
    upload_response = requests.post(
        '%s/upload' % settings.PRINT_SYSTEM_ADDRESS,
        files={'pdf': pdf_file},
        data={'type': 'translation'}
    )
    upload_response.raise_for_status()
    filename = upload_response.content
    response = requests.post(
        '%s/translation' % settings.PRINT_SYSTEM_ADDRESS,
        data={
            'filename': filename,
            'country_code': country_code,
            'country_name': country_name,
            'count': count
        }
    )
    response.raise_for_status()


def send_pdf_to_printer(pdf_file_path, count=1):
    pdf_file = open(pdf_file_path, 'rb')
    upload_response = requests.post(
        '%s/upload' % settings.PRINT_SYSTEM_ADDRESS,
        files={'pdf': pdf_file},
        data={'type': 'mass'}
    )
    upload_response.raise_for_status()
    filename = upload_response.content
    response = requests.post(
        '%s/mass' % settings.PRINT_SYSTEM_ADDRESS,
        data={
            'filename': filename,
            'count': count
        }
    )
    response.raise_for_status()
