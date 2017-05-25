import markdown
from django.core.mail.message import EmailMultiAlternatives
from django.http.response import HttpResponseRedirect

from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

from interp.utils import ISCEditorCheckMixin, AdminCheckMixin
from interp.models import Task, User, Contest, Translation

from wkhtmltopdf.views import PDFTemplateView


class Tasks(ISCEditorCheckMixin, View):
    def get(self, request):
        # questions = Task.objects.values_list('id', 'title', 'enabled')
        # TODO: need refactor (find can_publish_last_version by query)
        tasks = []
        for task in Task.objects.all():
            can_enable_task = (not task.enabled) and (task.versions.filter(released=True).first() is not None)
            tasks.append({'id': task.id, 'title': task.title, 'enabled': task.enabled, 'can_enable': can_enable_task, 'contest': task.contest.title})

        user = User.objects.get(username=request.user.username)
        contests = Contest.objects.order_by('order')
        return render(request, 'tasks.html',
                      context={'tasks': tasks, 'contests': contests, 'language': user.credentials()})

    def post(self, request):
        title = request.POST['title']
        contest_id = request.POST['contest']
        contest = Contest.objects.filter(id=contest_id).first()
        new_task = Task.objects.create(title=title, contest=contest)
        return redirect(to=reverse('edittask', kwargs={'id': new_task.id}))


class EditTask(ISCEditorCheckMixin, View):
    def get(self, request, id):
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        if not task.enabled:
            enabled = 'false'
        else:
            enabled = 'true'

        return render(request, 'editor-task.html',
                      context={'content': task.get_latest_text(), 'title': task.title, 'is_published': enabled,
                               'taskId': id, 'language': user.credentials()})


class SaveTask(ISCEditorCheckMixin, View):
    def post(self, request):
        id = request.POST['id']
        content = request.POST['content']
        title = request.POST['title']
        release_note = request.POST.get('change_log', "")
        publish_raw = request.POST.get('publish', 'false')
        released = False
        if publish_raw == 'true':
            released = True
        task = Task.objects.get(id=id)
        task.title = title
        task.save()
        task.add_version(content, release_note, released)
        return HttpResponse("done")


class EnableTask(ISCEditorCheckMixin, View):
    def post(self, request):
        id = request.POST['id']
        task = Task.objects.get(id=id)
        task.enabled = True
        task.save()
        return HttpResponse("Task has been unpublished!")

    def delete(self, request):
        id = request.GET['id']
        task = Task.objects.get(id=id)
        task.enabled = False
        task.save()
        return HttpResponse("Task has been unpublished!")


class TaskVersions(LoginRequiredMixin, View):
    def get(self, request, id):
        # TODO
        # published_raw = request.GET.get('published', 'false')
        # published = False
        # if published_raw == 'true':
        #     published = True
        user = User.objects.get(username=request.user.username)
        released = True
        if user.is_superuser or user.groups.filter(name="editor").exists():
            released = False
        task = Task.objects.get(id=id)
        versions_query = task.versions.order_by('-create_time')
        if released:
            versions_query = versions_query.filter(released=True)
        versions_values = versions_query.values('id', 'text', 'create_time', 'release_note')
        if request.is_ajax():
            return JsonResponse(dict(versions=list(versions_values)))
        else:
            return render(request, 'task_versions.html',
                          context={'task_title': task.title, 'versions': versions_values, 'quesId': id,})


class GetTaskPDF(LoginRequiredMixin, PDFTemplateView):
    filename = 'my_pdf.pdf'
    template_name = 'pdf_template.html'
    cmd_options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'footer-spacing': 3,
        'zoom': 15,
        'javascript-delay': 500,
    }

    def get_context_data(self, **kwargs):
        md = markdown.Markdown(extensions=['mdx_math'])
        context = super(GetTaskPDF, self).get_context_data(**kwargs)
        task_id = self.request.GET['id']
        task = Task.objects.filter(id=task_id).first()
        if task is None or task.enabled is False:
            # TODO
            return None

        self.filename = "%s-%s.pdf" % (task.title, 'original')
        content = task.get_latest_text()
        context['direction'] = 'ltr'
        context['content'] = content
        context['title'] = self.filename
        context['task_title'] = task.title
        context['country'] = "ISC"
        context['language'] = "en"
        context['contest'] = task.contest.title
        self.cmd_options['footer-center'] = '%s [page] / [topage]' % task.title
        return context


class MailTaskPDF(GetTaskPDF):
    def get(self, request, *args, **kwargs):
        response = super(MailTaskPDF, self).get(request, *args, **kwargs)
        response.render()

        subject, from_email, to = 'hello', 'navidsalehn@gmail.com', 'navidsalehn@gmail.com'
        text_content = 'Test'
        html_content = '<p>This is an <strong>TEST</strong> message.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.attach('file.pdf', response.content, 'application/pdf')
        msg.send()

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
