import markdown
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from django.http.response import HttpResponseRedirect, HttpResponseNotFound
from django.urls.base import reverse
from django.utils import timezone

from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from trans.models import User, Task, Translation, ContentVersion, VersionParticle, Contest
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse

from wkhtmltopdf.views import PDFTemplateView

from trans.models import FlatPage
from trans.forms import UploadFileForm
from trans.utils import get_translate_edit_permission, can_save_translate, is_translate_in_editing, CONTEST_ORDER, \
    unleash_edit_translation_token, get_task_by_contest_and_name, get_trans_by_user_and_task, \
    can_user_change_translation


class Home(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        home_flat_page = FlatPage.objects.filter(slug="home").first()
        home_content = home_flat_page.content if home_flat_page else ''
        tasks_by_contest = {contest: [] for contest in Contest.objects.all()}
        for task in Task.objects.filter(contest__public=True):
            translation = Translation.objects.filter(user=user, task=task).first()
            is_editing = translation and is_translate_in_editing(translation)
            frozen = translation and translation.frozen
            tasks_by_contest[task.contest].append(
                {'id': task.id, 'name': task.name, 'is_editing': is_editing, 'frozen': frozen})
        tasks_lists = [{'title': c.title, 'slug': c.slug, 'tasks': tasks_by_contest[c]} for c in
                       Contest.objects.order_by('-order') if
                       len(tasks_by_contest[c]) > 0]
        return render(request, 'translations.html', context={'tasks_lists': tasks_lists, 'home_content': home_content,
                                                           'language': user.credentials()})


class Translations(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user)
        try:
            task = get_task_by_contest_and_name(contest_slug, task_name)
        except Exception as e:
            return HttpResponseBadRequest(e.message)
        trans = get_trans_by_user_and_task(user, task)
        if trans.frozen:
            return HttpResponseForbidden("This task is frozen")
        task_text = task.get_published_text()
        return render(request, 'translation.html',
                      context={'trans': trans.get_latest_text(), 'task': task_text, 'rtl': user.language.rtl,
                               'text_font_base64': user.text_font_base64, 'contest_slug': contest_slug,
                               'task_name': task_name,
                               'quesId': task.id, 'language': user.credentials()})


class SaveTranslation(LoginRequiredMixin, View):
    def post(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user)
        try:
            task = get_task_by_contest_and_name(contest_slug, task_name)
        except Exception as e:
            return HttpResponseBadRequest(e.message)
        translation = get_trans_by_user_and_task(user, task)
        content = request.POST['content']
        edit_token = request.POST.get('edit_token', '')
        if not can_user_change_translation(user, translation, edit_token):
            return JsonResponse({'can_edit': False, 'edit_token': '', 'error': 'forbidden'})
        translation.add_version(content)
        VersionParticle.objects.filter(translation=translation).delete()
        return JsonResponse({'success': True})


class SaveVersionParticle(LoginRequiredMixin, View):
    def post(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user)
        try:
            task = get_task_by_contest_and_name(contest_slug, task_name)
        except Exception as e:
            return HttpResponseBadRequest(e.message)
        translation = get_trans_by_user_and_task(user, task)
        content = request.POST['content']
        edit_token = request.POST.get('edit_token', '')
        if not can_user_change_translation(user, translation, edit_token):
            return JsonResponse({'can_edit': False, 'edit_token': '', 'error': 'forbidden'})
        if translation.get_latest_text().strip() == content.strip():
            return JsonResponse({'can_edit': True, 'edit_token': edit_token, 'error': 'Not Modified'})
        last_version_particle = translation.versionparticle_set.order_by('-create_time').first()
        if last_version_particle:
            last_version_particle.text = content
            last_version_particle.save()
        else:
            last_version_particle = VersionParticle.objects.create(translation=translation, text=content,
                                                                   create_time=timezone.now())
        return JsonResponse({'success': True})


class GetTranslatePreview(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user)
        try:
            task = get_task_by_contest_and_name(contest_slug, task_name)
        except Exception as e:
            return HttpResponseBadRequest(e.message)
        translation = get_trans_by_user_and_task(user, task)
        # TODO check if it's available
        direction = 'rtl' if translation.user.language.rtl else 'ltr'
        return render(request, 'pdf-template.html', context={'content': translation.get_latest_text(),
                                                             'direction': direction,
                                                             'task_name': "%s-%s" % (
                                                             task.name, translation.user.language),
                                                             'text_font_base64': user.text_font_base64,
                                                             'country': translation.user.country.name,
                                                             'language': translation.user.language.name,
                                                             'contest': translation.task.contest.title})


class UserFont(LoginRequiredMixin, View):
    def get(self, request):
        user = User.objects.get(username=request.user)
        return render(request, 'font.css', content_type='text/css', context={'text_font_base64': user.text_font_base64})

class TranslationMarkdown(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user)
        version_id = request.GET.get('ver')
        if version_id:
            content_version = ContentVersion.objects.filter(id=version_id).first()
            if not content_version.can_view_by(user):
                return None
            content = content_version.text
        else:
            try:
                task = get_task_by_contest_and_name(contest_slug, task_name)
            except Exception as e:
                return HttpResponseBadRequest(e.message)
            translation = get_trans_by_user_and_task(user, task)
            content = translation.get_latest_text()

        return HttpResponse(content, content_type='text/plain; charset=UTF-8')


class TranslationPDF(LoginRequiredMixin, PDFTemplateView):
    filename = 'my_pdf.pdf'
    template_name = 'pdf-template.html'
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
        context = super(TranslationPDF, self).get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user)
        version_id = self.request.GET.get('ver')
        contest_slug = kwargs['contest_slug']
        task_name = kwargs['task_name']
        try:
            task = get_task_by_contest_and_name(contest_slug, task_name)
        except Exception as e:
            return HttpResponseBadRequest(e.message)
        trans = get_trans_by_user_and_task(user, task)

        if version_id:
            content_version = ContentVersion.objects.filter(id=version_id).first()
            if not content_version.can_view_by(user):
                return None
            content = content_version.text
            file_name = "%s-%s-%d.pdf" % (task.name, trans.user.language, version_id)
        else:
            content = trans.get_latest_text()
            file_name = "%s-%s.pdf" % (task.name, trans.user.language)

        trans = get_trans_by_user_and_task(user, task)
        self.filename = file_name
        context['direction'] = 'rtl' if trans.user.language.rtl else 'ltr'
        context['content'] = content
        context['title'] = self.filename
        context['task_name'] = trans.task.name
        context['country'] = trans.user.country.name
        context['language'] = trans.user.language.name
        context['contest'] = trans.task.contest.title
        context['text_font_base64'] = trans.user.text_font_base64
        self.cmd_options['footer-center'] = '%s [page] / [topage]' % trans.task.name
        return context


class AccessTranslationEdit(LoginRequiredMixin, View):
    def post(selfs, request, id):
        edit_token = request.POST.get('edit_token', '')
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user)
        if not task.contest.public:
            return HttpResponseBadRequest("There is no published task")
        translation = Translation.objects.get(user=user, task=task)
        if user != translation.user:
            return HttpResponseForbidden()
        can_edit, new_edit_token = get_translate_edit_permission(translation, edit_token)
        return JsonResponse({'can_edit': can_edit, 'edit_token': new_edit_token})


# TODO
class FinishTranslate(LoginRequiredMixin, View):
    def post(self, request, id):
        user = User.objects.get(username=request.user)
        task = Task.objects.get(id=id)
        trans = Translation.objects.get(user=user, task=task)
        edit_token = request.POST.get('edit_token', '')
        if trans is None:
            return HttpResponseNotFound("There is no task")
        if not trans.user == user and can_save_translate(trans, edit_token):
            return HttpResponseForbidden("You don't have acccess")
        unleash_edit_translation_token(trans)
        return JsonResponse({'message': "Done"})


class CheckTranslationEditAccess(LoginRequiredMixin, View):
    def post(selfs, request, id):
        edit_token = request.POST.get('edit_token', '')
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user)
        if not task.contest.public:
            return HttpResponseBadRequest("There is no published task")
        translation = Translation.objects.get(user=user, task=task)
        if user != translation.user:
            return HttpResponseForbidden()
        return JsonResponse({'is_editing': can_save_translate(translation, edit_token)})


class TranslatePreview(LoginRequiredMixin, View):
    def get(self, request, id):
        user = User.objects.get(username=request.user)
        task = Task.objects.get(id=id)
        if task.contest.public == False:
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


class CheckoutVersion(LoginRequiredMixin, View):
    def post(self, request):
        version_id = self.request.POST['id']
        content_version = ContentVersion.objects.filter(id=version_id).first()
        user = User.objects.get(username=request.user)
        translation = content_version.content_object
        if user != translation.user or translation.frozen:
            return JsonResponse({'error': 'forbidden'})
        translation.add_version(content_version.text)
        VersionParticle.objects.filter(translation=translation).delete()
        return JsonResponse({'message': 'Done'})


class Versions(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user)
        contest = Contest.objects.filter(slug=contest_slug).first()
        if not contest:
            return HttpResponseNotFound("There is no contest")
        task = Task.objects.get(name=task_name, contest=contest)
        try:
            trans = Translation.objects.get(user=user, task=task)
        except:
            trans = Translation.objects.create(user=user, task=task)
            trans.add_version(task.get_published_text())

        v = []
        vp = []
        versions = trans.versions.all().order_by('-create_time')
        version_particles = VersionParticle.objects.filter(translation=trans).order_by('-create_time')
        for item in version_particles:
            vp.append((item.id, item.create_time))
        for item in versions:
            v.append((item.id, item.create_time))

        if request.is_ajax():
            return JsonResponse(dict(versions=list(v), version_particles=list(vp)))
        else:
            return render(request, 'revisions.html',
                          context={'versions': v, 'versionParticles': vp, 'translation': trans.get_latest_text(),
                                   'quesId': trans.id, 'task_name': task.name, 'contest_slug': contest_slug})


class GetVersion(LoginRequiredMixin, View):
    def get(self, request):
        id = request.GET['id']
        version = ContentVersion.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        if version.content_type.model != 'translation' or version.content_object.user != user:
            return HttpResponseBadRequest()
        return HttpResponse(version.text)


class GetVersionParticle(LoginRequiredMixin, View):
    def get(self, request):
        id = request.GET['id']
        version_particle = VersionParticle.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        if version_particle.translation.user != user:
            return HttpResponseForbidden()
        return HttpResponse(version_particle.text)


class GetTranslatePDF(LoginRequiredMixin, PDFTemplateView):
    filename = 'my_pdf.pdf'
    template_name = 'pdf-template.html'
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
        print(kwargs)
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

        self.filename = "%s-%s.pdf" % (task.name, trans.user.language)
        content = trans.get_latest_text()
        context['direction'] = 'rtl' if trans.user.language.rtl else 'ltr'
        context['content'] = content
        context['title'] = self.filename
        context['task_name'] = trans.task.name
        context['country'] = trans.user.country.name
        context['language'] = trans.user.language.name
        context['contest'] = trans.task.contest.title
        context['text_font_base64'] = user.text_font_base64
        self.cmd_options['footer-center'] = '%s [page] / [topage]' % trans.task.name
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
        return render(request, 'custom-print.html', {'form': form})

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
