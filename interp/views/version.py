import markdown
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse, HttpResponseForbidden
from django.views.generic.base import View
from wkhtmltopdf.views import PDFTemplateView

from interp.models import User, ContentVersion, Translation, Task


class VersionDownloadMixin(object):
    def get_file_format(self):
        return self.file_format

    def get_version(self):
        version_id = self.request.GET['id']
        content_version = ContentVersion.objects.filter(id=version_id).first()
        return content_version

    # TODO I MUST refactor this method
    def get_version_text(self):
        content_type_model = self.request.GET.get('type', None)
        id = self.request.GET['id']
        user = User.objects.get(username=self.request.user.username)
        if content_type_model:
            task = Task.objects.filter(id=id).first()
            if task is None or task.enabled == False:
                return None
            if content_type_model == 'translation':
                translation = Translation.objects.filter(user=user, task=task).first()
                if translation is None or translation.user != user:
                    return None
                return translation.get_latest_text()
            elif content_type_model == 'task':
                return task.get_published_text()
            else:
                return None

        content_version = ContentVersion.objects.filter(id=id).first()
        if not content_version.can_view_by(user):
            return None
        return content_version.text

    # TODO I MUST refactor this method
    def get_filename(self):
        # version = self.get_version()
        # obj = version.content_object
        # created = version.create_time
        # return "%s_%d-%d-%d %d:%d.%s" % (obj.title, created.year, created.month, created.day,
        #                                   created.hour, created.minute, self.get_file_format())
        content_type_model = self.request.GET.get('type', None)
        id = self.request.GET['id']
        user = User.objects.get(username=self.request.user.username)
        if content_type_model:
            task = Task.objects.filter(id=id).first()
            if task is None or task.enabled == False:
                return None
            if content_type_model == 'translation':
                translation = Translation.objects.filter(user=user, task=task).first()
                if translation is None or translation.user != user:
                    return None
                return "%s-%s-%s.%s" % (
                task.title, translation.user.language, translation.get_latest_change_time(), self.get_file_format())
            elif content_type_model == 'task':
                return "%s-%s-%s.%s" % (task.title, "ISC", task.get_latest_change_time(), self.get_file_format())
            else:
                return None

        content_version = ContentVersion.objects.filter(id=id).first()
        if not content_version.can_view_by(user):
            return None
        if content_version.content_type.model == "translation":
            return "%s-%s-%s.%s" % (
                content_version.content_object.task.title, content_version.content_object.user.language,
                content_version.content_object.get_latest_change_time(), self.get_file_format())
        else:
            return "%s-%s-%s.%s" % (
                content_version.content_object.title, "ISC", content_version.content_object.get_latest_change_time(),
                self.get_file_format())


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
        # version = self.get_version()
        #
        # content = version.text
        content = self.get_version_text()
        context['direction'] = 'ltr'
        context['content'] = content
        context['title'] = self.get_filename()
        return context


class GetVersionMarkDown(VersionDownloadMixin, LoginRequiredMixin, View):
    file_format = 'md'

    def get(self, request, *args, **kwargs):
        # version = self.get_version()
        # user = User.objects.get(username=self.request.user.username)
        # if version.can_view_by(user) == False:
        #     HttpResponseForbidden()

        content = self.get_version_text()
        response = HttpResponse(content, content_type='text/markdown; charset=UTF-8')
        return response
