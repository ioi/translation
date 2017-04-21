import markdown
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.views.generic.base import View
from wkhtmltopdf.views import PDFTemplateView

from interp.models import ContentVersion


class VersionDownloadMixin(object):
    def get_file_format(self):
        return self.file_format

    def get_version(self):
        task_id = self.request.GET['id']
        content_version = ContentVersion.objects.filter(id=task_id).first()
        return content_version

    def get_filename(self):
        version = self.get_version()
        obj = version.content_object
        created = version.create_time
        return "%s_%d-%d-%d %d:%d.%s" % (obj.title, created.year, created.month, created.day,
                                          created.hour, created.minute, self.get_file_format())


class GetVersionPDF(VersionDownloadMixin, LoginRequiredMixin, PDFTemplateView):
    file_format = 'pdf'
    template_name = 'pdf_template.html'
    cmd_options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        # 'zoom': 15,
        'javascript-delay': 500,
    }

    def get_context_data(self, **kwargs):
        context = super(GetVersionPDF, self).get_context_data(**kwargs)
        version = self.get_version()

        content = version.text
        context['direction'] = 'ltr'
        context['content'] = content
        context['title'] = self.get_filename()
        return context


class GetVersionMarkDown(VersionDownloadMixin, LoginRequiredMixin, View):
    file_format = 'md'

    def get(self, request, *args, **kwargs):
        version = self.get_version()

        content = version.text
        response = HttpResponse(content, content_type='text/markdown; charset=UTF-8')
        response['Content-Disposition'] = 'attachment; filename=%s' % self.get_filename()
        return response
