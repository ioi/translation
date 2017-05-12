import markdown
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from django.http.response import HttpResponseRedirect, HttpResponseNotFound
from django.urls.base import reverse
from django.utils import timezone

from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from interp.models import User, Task, Translation, ContentVersion, VersionParticle, Contest
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse

from wkhtmltopdf.views import PDFTemplateView

from interp.models import FlatPage
from interp.forms import UploadFileForm
from interp.utils import get_translate_edit_permission, can_save_translate, is_translate_in_editing, CONTEST_ORDER, \
    unleash_edit_translation_token


class Home(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        # tasks = Task.objects.filter(enabled=True).values_list('id', 'title')
        tasks = []
        home_flat_page = FlatPage.objects.filter(slug="home").first()
        home_content = home_flat_page.content if home_flat_page else ''
        tasks_by_contest = {contest: [] for contest in Contest.objects.all()}
        for task in Task.objects.filter(enabled=True):
            translation = Translation.objects.filter(user=user, task=task).first()
            is_editing = translation and is_translate_in_editing(translation)
            freezed = translation and translation.freezed
            tasks_by_contest[task.contest].append((task.id, task.title, is_editing, freezed))
            tasks.append((task.id, task.title, is_editing, freezed))
        tasks_lists = [(c.title, c.slug, tasks_by_contest[c]) for c in Contest.objects.order_by('-order') if
                           len(tasks_by_contest[c]) > 0]
        return render(request, 'questions.html', context={'tasks_lists': tasks_lists, 'home_content': home_content,
                                                          'language': user.credentials()})


class Questions(LoginRequiredMixin,View):
    def get(self,request, contest_slug, task_title):
        user = User.objects.get(username=request.user)
        contest = Contest.objects.filter(slug=contest_slug).first()
        if not contest:
            return HttpResponseNotFound("There is no contest")
        task = Task.objects.get(title=task_title, contest=contest)
        if not task.enabled:
            return HttpResponseBadRequest("There is no published task")
        task_text = task.get_published_text()
        try:
            trans = Translation.objects.get(user=user, task=task)
        except:
            trans = Translation.objects.create(user=user, task=task)
            trans.add_version(task_text)
        if trans.freezed:
            return HttpResponseForbidden("This task is freezed")
        return render(request, 'editor.html',
                          context={'trans': trans.get_latest_text(), 'task': task_text, 'rtl': user.language.rtl,
                                   'text_font_base64': user.text_font_base64,
                                   'quesId': task.id, 'language': user.credentials()})


class AccessTranslationEdit(LoginRequiredMixin, View):
    def post(selfs, request, id):
        edit_token = request.POST.get('edit_token', '')
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user)
        if not task.enabled:
            return HttpResponseBadRequest("There is no published task")
        translation = Translation.objects.get(user=user, task=task)
        if user != translation.user:
            return HttpResponseForbidden()
        can_edit, new_edit_token = get_translate_edit_permission(translation, edit_token)
        return JsonResponse({'can_edit': can_edit, 'edit_token': new_edit_token})


#TODO
class UnleashEditTranslationToken(LoginRequiredMixin, View):
    def post(self, request, id):
        user = User.objects.get(username=request.user)
        task = Task.objects.get(id=id)
        trans = Translation.objects.get(user=user, task=task)
        edit_token = request.POST.get('edit_token', '')
        if trans is None:
            return HttpResponseNotFound("There is no task")
        if not (user.is_superuser or user.groups.filter(name="staff").exists() or (
                trans.user == user and can_save_translate(trans, edit_token))):
            return HttpResponseForbidden("You don't have acccess")
        unleash_edit_translation_token(trans)
        return redirect(to=reverse('user_trans', kwargs={'username': trans.user.username}))


class CheckTranslationEditAccess(LoginRequiredMixin, View):
    def post(selfs, request, id):
        edit_token = request.POST.get('edit_token', '')
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user)
        if not task.enabled:
            return HttpResponseBadRequest("There is no published task")
        translation = Translation.objects.get(user=user, task=task)
        if user != translation.user:
            return HttpResponseForbidden()
        return JsonResponse({'is_editing': can_save_translate(translation, edit_token)})


class TranslatePreview(LoginRequiredMixin,View):
    def get(self,request,id):
        user = User.objects.get(username=request.user)
        task = Task.objects.get(id=id)
        if task.enabled == False:
            return HttpResponseBadRequest("There is no published task")
        task_text = task.get_published_text()
        try:
            trans = Translation.objects.get(user=user, task=task)
        except:
            trans = Translation.objects.create(user=user, task=task)
            trans.add_version(task_text)

        return render(request, 'preview.html',
                          context={'trans': trans.get_latest_text(), 'task': task_text, 'rtl': user.language.rtl,
                                   'quesId': id,
                                   'text_font_base64': user.text_font_base64,
                                   'language': user.credentials()})


class SaveQuestion(LoginRequiredMixin,View):
    def post(self,request):
        id = request.POST['id']
        content = request.POST['content']
        edit_token = request.POST.get('edit_token', '')
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user)
        translation = Translation.objects.get(user=user,task=task)
        if user != translation.user or not can_save_translate(translation, edit_token) or translation.freezed:
            return JsonResponse({'can_edit': False, 'edit_token': '', 'error': 'forbidden'})
        translation.add_version(content)
        VersionParticle.objects.filter(translation=translation).delete()
        return JsonResponse({'success': True})


class CheckoutVersion(LoginRequiredMixin,View):
    def post(self,request):
        version_id = self.request.POST['id']
        content_version = ContentVersion.objects.filter(id=version_id).first()
        user = User.objects.get(username=request.user)
        translation = content_version.content_object
        if user != translation.user or translation.freezed:
            return JsonResponse({'error': 'forbidden'})
        translation.add_version(content_version.text)
        VersionParticle.objects.filter(translation=translation).delete()
        return JsonResponse({'message': 'Done'})


class Versions(LoginRequiredMixin,View):
    def get(self,request, contest_slug, task_title):
        user = User.objects.get(username=request.user)
        contest = Contest.objects.filter(slug=contest_slug).first()
        if not contest:
            return HttpResponseNotFound("There is no contest")
        task = Task.objects.get(title=task_title, contest=contest)
        try:
            trans = Translation.objects.get(user=user,task=task)
        except:
            trans = Translation.objects.create(user=user, task=task)
            trans.add_version(task.get_published_text())

        v = []
        vp = []
        versions = trans.versions.all().order_by('-create_time')
        version_particles = VersionParticle.objects.filter(translation=trans).order_by('-create_time')
        for item in version_particles:
            vp.append((item.id,item.create_time))
        for item in versions:
            v.append((item.id,item.create_time))

        if request.is_ajax():
            return JsonResponse(dict(versions=list(v), version_particles=list(vp)))
        else:
            return render(request, 'versions.html',
                      context={'versions': v, 'versionParticles': vp, 'translation': trans.get_latest_text(),
                               'quesId': trans.id, 'taskTitle': task.title, 'contest_slug': contest_slug})


class GetVersion(LoginRequiredMixin,View):
    def get(self,request):
        id = request.GET['id']
        version = ContentVersion.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        if version.content_type.model != 'translation' or version.content_object.user != user:
            return HttpResponseBadRequest()
        return HttpResponse(version.text)


class GetVersionParticle(LoginRequiredMixin,View):
    def get(self,request):
        id = request.GET['id']
        version_particle = VersionParticle.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        if version_particle.translation.user != user:
            return HttpResponseForbidden()
        return HttpResponse(version_particle.text)


class SaveVersionParticle(LoginRequiredMixin,View):
    def post(self,request):
        id = request.POST['id']
        content = request.POST['content']
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        edit_token = request.POST.get('edit_token', '')
        translation = Translation.objects.get(user=user, task=task)
        if user != translation.user or not can_save_translate(translation, edit_token) or translation.freezed:
            return JsonResponse({'can_edit': False, 'edit_token': '', 'error': 'forbidden'})
        if translation.get_latest_text().strip() == content.strip():
            return JsonResponse({'can_edit': False, 'edit_token': '', 'error': 'Not Modified'})
        last_version_particle = translation.versionparticle_set.order_by('-create_time').first()
        if last_version_particle:
            last_version_particle.text = content
            last_version_particle.save()
        else:
            last_version_particle = VersionParticle.objects.create(translation=translation, text=content,
                                                                   create_time=timezone.now())
        return JsonResponse({'success': True})


class GetTranslatePreview(LoginRequiredMixin,View):
    def get(self,request):
        task_id = self.request.GET['id']
        task = Task.objects.get(id=task_id)
        user = User.objects.get(username=request.user.username)
        translation = Translation.objects.get(user=user, task=task)
        # TODO check if it's available
        direction = 'rtl' if translation.user.language.rtl else 'ltr'
        return render(request, 'pdf_template.html', context={'content': translation.get_latest_text(),\
                    'direction': direction, 'title': "%s-%s" % (task.title, translation.user.language)})


class GetTranslatePDF(LoginRequiredMixin, PDFTemplateView):
    filename = 'my_pdf.pdf'
    template_name = 'pdf_template.html'
    cmd_options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'footer-spacing': 3,
        # 'zoom': 15,
        'javascript-delay': 500,
    }

    def get_context_data(self, **kwargs):
        context = super(GetTranslatePDF, self).get_context_data(**kwargs)
        task_id = self.request.GET['id']

        user = User.objects.get(username=self.request.user.username)
        task = Task.objects.filter(id=task_id).first()
        if task is None:
            # TODO
            return None

        trans = Translation.objects.filter(user=user, task=task).first()
        if trans is None:
            # TODO
            return None

        self.filename = "%s-%s.pdf" % (task.title, trans.user.language)
        content = trans.get_latest_text()
        context['direction'] = 'rtl' if trans.user.language.rtl else 'ltr'
        context['content'] = content
        context['title'] = self.filename
        context['task_title'] = trans.task.title
        context['country'] = trans.user.country.name
        context['language'] = trans.user.language.name
        context['contest'] = trans.task.contest.title
        context['text_font_base64'] = user.text_font_base64
        self.cmd_options['footer-center'] = '%s [page] / [topage]' % trans.task.title
        return context


class MailTranslatePDF(GetTranslatePDF):
    def get(self, request, *args, **kwargs):
        response = super(MailTranslatePDF, self).get(request, *args, **kwargs)
        response.render()

        subject, from_email, to = 'hello', 'navidsalehn@gmail.com', 'navidsalehn@gmail.com'
        text_content = 'Test'
        html_content = '<p>This is an <strong>TEST</strong> message.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.attach('file.pdf', response.content, 'application/pdf')
        msg.send()

        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class PrintCustomFile(LoginRequiredMixin, View):
    def get(self, request):
        form = UploadFileForm()
        return render(request, 'print_custom_file.html', {'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest("You should attach a file")
        pdf_file = request.FILES['pdf_file']
        if not pdf_file:
            return HttpResponseBadRequest("You should attach a file")
        pdf_file = pdf_file.read()
        subject, from_email, to = 'hello', 'navidsalehn@gmail.com', 'navidsalehn@gmail.com'
        text_content = 'Test'
        html_content = '<p>This is an <strong>TEST</strong> message.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.attach('file.pdf', pdf_file, 'application/pdf')
        msg.send()

        return HttpResponseRedirect(request.META['HTTP_REFERER'])