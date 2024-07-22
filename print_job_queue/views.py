from collections import defaultdict
import logging

from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q

from print_job_queue import models, queue

logger = logging.getLogger(__name__)


class StaffCheckMixin(LoginRequiredMixin, object):
    user_check_failure_path = '/'

    def check_user(self, user):
        return user.is_superuser or user.groups.filter(name="staff").exists()

    def user_check_failed(self, request, *args, **kwargs):
        logger.warning(f'Staff check failed for user {request.user.username}')
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            return self.user_check_failed(request, *args, **kwargs)
        return super(StaffCheckMixin, self).dispatch(request, *args, **kwargs)


class JobQueue(StaffCheckMixin, View):
    def get(self, request, group, job_type, worker_name=None):
        job_type_enum = _parse_job_type(job_type)

        if worker_name:
            worker = _parse_worker(worker_name)
            jobs = queue.query_worker_print_jobs(group, job_type_enum, worker)
            workers = None
        else:
            worker = None
            jobs = queue.query_group_print_jobs(group, job_type_enum)
            workers = models.Worker.objects.filter(Q(job_type=None) | Q(job_type=job_type_enum.value)).order_by('name')

        job_info_by_state = defaultdict(list)
        for job in jobs:
            job_info_by_state[models.STATE_BY_VALUE[job.state].name].append({
                'id': job.id,
                'owner': job.owner.username,
                'documents': [(document.file_path, document.print_count)
                              for document in job.document_set.all()],
                'worker': job.worker,
            })

        return render(request, 'queue.html',
                      context={
                          'group': group,
                          'job_type': job_type,
                          'type_header': 'Final Translations' if job_type_enum == models.PrintJobType.FINAL else "Draft Translations",
                          'worker': worker,
                          'workers': workers,
                          'job_info_by_state': job_info_by_state,
                          'job_states': [
                              ('Pending', 'PENDING'),
                              ('In progress', 'IN_PROGRESS'),
                              ('Printing', 'PRINTING'),
                              ('Done', 'DONE'),
                          ],
                      })


class JobPickUp(StaffCheckMixin, View):
    @transaction.atomic
    def post(self, request, worker_name, job_id, job_action):
        worker = _parse_worker(worker_name)
        do_print = job_action == 'print'

        job = queue.pick_up_print_job(job_id=job_id, worker=worker, do_print=do_print)
        if job is None:
            return HttpResponseBadRequest(
                'Could not pick up job. Check log for more details.')

        http_referer = request.headers.get('referer')
        if http_referer:
            return redirect(http_referer)
        return HttpResponse('Ok!')


class JobMarkCompletion(StaffCheckMixin, View):
    @transaction.atomic
    def post(self, request, worker_name, job_id):
        worker = _parse_worker(worker_name)

        if not queue.mark_print_job_complete(job_id=job_id, worker=worker):
            return HttpResponseBadRequest(
                'Could not mark job as complete. Check log for more details.')

        http_referer = request.headers.get('referer')
        if http_referer:
            return redirect(http_referer)
        return HttpResponse('Ok!')


class JobRestart(StaffCheckMixin, View):
    @transaction.atomic
    def post(self, request, job_id):
        if not queue.restart_print_job(job_id=job_id):
            return HttpResponseBadRequest(
                'Could not restart job. Check log for more details.')

        http_referer = request.headers.get('referer')
        if http_referer:
            return redirect(http_referer)
        return HttpResponse('Ok!')


def _parse_job_type(job_type):
    try:
        return models.PrintJobType[job_type.upper()]
    except KeyError:
        raise Http404("Unknown job type")


def _parse_worker(worker_name):
    worker = models.Worker.objects.filter(name=worker_name).first()
    if worker:
        return worker
    else:
        raise Http404("Unknown worker")
