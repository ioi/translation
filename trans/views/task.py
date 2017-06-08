import markdown
from django.core.mail.message import EmailMultiAlternatives
from django.http.response import HttpResponseRedirect, HttpResponseForbidden

from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

from trans.utils import get_task_by_contest_and_name, is_translate_in_editing, get_trans_by_user_and_task
from trans.models import Task, User, Contest, Translation, ContentVersion
from trans.views.admin import ISCEditorCheckMixin

from wkhtmltopdf.views import PDFTemplateView


class Tasks(ISCEditorCheckMixin, View):
    def get(self, request):
        # TODO: need refactor
        if request.user.username != "ISC":
            return HttpResponseForbidden("You don't have access to this page")

        user = User.objects.get(username=request.user.username)
        tasks_by_contest = {contest: [] for contest in Contest.objects.all()}
        for task in Task.objects.all():
            translation = Translation.objects.filter(user=user, task=task).first()
            is_editing = translation and is_translate_in_editing(translation)
            frozen = translation and translation.frozen
            tasks_by_contest[task.contest].append(
                {'id': task.id, 'name': task.name, 'is_editing': is_editing, 'frozen': frozen})
        tasks_lists = [{'title': c.title, 'slug': c.slug, 'tasks': tasks_by_contest[c]} for c in
                       Contest.objects.order_by('-order') if
                       len(tasks_by_contest[c]) > 0]
        contests = Contest.objects.order_by('order')
        return render(request, 'tasks.html',
                      context={'tasks_lists': tasks_lists, 'contests': contests, 'language': user.credentials()})

    def post(self, request):
        if request.user.username != "ISC":
            return HttpResponseForbidden("You don't have access to this page")
        name = request.POST['name']
        name = name.replace(' ', '').replace('/','')
        contest_id = request.POST['contest']
        contest = Contest.objects.filter(id=contest_id).first()
        new_task, created = Task.objects.get_or_create(name=name, contest=contest)
        if not created:
            return HttpResponseBadRequest("This task is duplicate")
        user = User.objects.get(username=request.user.username)
        new_trans = get_trans_by_user_and_task(user, new_task)
        return redirect(to=reverse('edit_translation', kwargs={'contest_slug': contest.slug, 'task_name': new_task.name}))


class ReleaseTask(ISCEditorCheckMixin, View):
    def post(self, request, contest_slug, task_name):
        release_note = request.POST.get('release_note', '')
        task = Task.objects.get(name=task_name, contest__slug=contest_slug)
        if task.frozen:
            return HttpResponseBadRequest("The task is frozen")
        task.publish_latest(release_note)
        return HttpResponse("done")


class TaskMarkdown(LoginRequiredMixin,View):
    def get(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user)
        version_id = request.GET.get('ver')
        if version_id:
            content_version = ContentVersion.objects.filter(id=version_id).first()
            if not content_version.can_view_by(user):
                return None
            content = content_version.text
        else:
            task = Task.objects.get(name=task_name, contest__slug=contest_slug)
            if user.is_editor():
                content = task.get_latest_text()
            else:
                content = task.get_published_text()
        return HttpResponse(content, content_type='text/plain; charset=UTF-8')


class TaskPDF(LoginRequiredMixin, PDFTemplateView):
    filename = 'my_pdf.pdf'
    template_name = 'pdf-template.html'
    cmd_options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'footer-spacing': 3,
        # 'zoom': 15,
        'javascript-delay': 500,
    }

    def get_context_data(self, **kwargs):
        context = super(TaskPDF, self).get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user)
        version_id = self.request.GET.get('ver')
        contest_slug = kwargs['contest_slug']
        task_name = kwargs['task_name']
        task = Task.objects.get(name=task_name, contest__slug=contest_slug)

        if version_id:
            content_version = ContentVersion.objects.filter(id=version_id).first()
            if not content_version.can_view_by(user):
                return None
            content = content_version.text
            file_name = "%s-%s-%d.pdf" % (task.name, "ISC", version_id)
        else:
            if user.is_editor():
                content = task.get_latest_text()
            else:
                content = task.get_published_text()
            file_name = "%s-%s.pdf" % (task.name, "ISC")

        self.filename = file_name
        context['direction'] = 'ltr'
        context['content'] = content
        context['title'] = self.filename
        context['task_name'] = task.name
        context['country'] = "ISC"
        context['language'] = "en"
        context['contest'] = task.contest.title
        self.cmd_options['footer-center'] = '%s [page] / [topage]' % task.name
        return context


class TaskVersions(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name):
        # TODO
        # published_raw = request.GET.get('published', 'false')
        # published = False
        # if published_raw == 'true':
        #     published = True
        user = User.objects.get(username=request.user.username)
        released = True
        if user.is_editor():
            released = False
        task = Task.objects.get(name=task_name, contest__slug=contest_slug)
        ISC_translation = task.get_corresponding_translation()
        versions_query = ISC_translation.versions.order_by('-create_time')
        if released:
            versions_query = versions_query.filter(released=True)
        versions_values = versions_query.values('id', 'text', 'create_time', 'release_note')
        if request.is_ajax():
            return JsonResponse(dict(versions=list(versions_values)))
        else:
            return render(request, 'task-revisions.html',
                          context={'task_name': task.name, 'contest_slug': contest_slug,
                                   'versions': versions_values, 'direction': 'ltr'})


#TODO: It's useless now
class EnableTask(ISCEditorCheckMixin, View):
    def post(self, request):
        id = request.POST['id']
        task = Task.objects.get(id=id)
        task.enabled = True
        task.save()
        return HttpResponse("Task has been published!")

    def delete(self, request):
        id = request.GET['id']
        task = Task.objects.get(id=id)
        task.enabled = False
        task.save()
        return HttpResponse("Task has been unpublished!")



class GetTaskPDF(LoginRequiredMixin, PDFTemplateView):
    filename = 'my_pdf.pdf'
    template_name = 'pdf-template.html'
    cmd_options = {
        'page-size': 'A4',
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
        if task is None or task.contest.public is False:
            # TODO
            return None

        self.filename = "%s-%s.pdf" % (task.name, 'original')
        content = task.get_latest_text()
        context['direction'] = 'ltr'
        context['content'] = content
        context['title'] = self.filename
        context['task_name'] = task.name
        context['country'] = "ISC"
        context['language'] = "en"
        context['contest'] = task.contest.title
        self.cmd_options['footer-center'] = '%s [page] / [topage]' % task.name
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
