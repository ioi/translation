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
