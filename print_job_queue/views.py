from collections import defaultdict
import logging
import os

from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.views import View

from print_job_queue import models, queue

logger = logging.getLogger(__name__)


class _PrintJobQueueView(View):

    print_job_model_cls = None
    template_file = None

    def get(self, request):
        assert self.print_job_model_cls is not None
        assert self.template_file is not None

        worker_name = request.GET.get('name', '')
        if not worker_name:
            return HttpResponseBadRequest('Worker name must be non-empty.')

        worker_count = _try_parse_int(request.GET.get('count'), 0)
        if worker_count <= 0:
            return HttpResponseBadRequest('Worker count must be positive.')

        worker_mod = _try_parse_int(request.GET.get('mod'), -1)
        if worker_mod < 0 or worker_mod >= worker_count:
            return HttpResponseBadRequest('Worker mod is out of range.')

        jobs = defaultdict(list)
        for job in queue.query_print_jobs(
                print_job_model_cls=self.print_job_model_cls,
                worker_name=worker_name,
                worker_mod=worker_mod,
                worker_count=worker_count):
            jobs[job.state].append({
                'id':
                    job.job_id,
                'owner':
                    job.owner.username,
                'documents': [(document.file_path, document.print_count)
                              for document in job.document_set.all()],
            })

        logger.info('jobs = %s', jobs)

        return render(request,
                      self.template_file,
                      context={
                          'in_progress_jobs':
                              jobs[models.PrintJobState.IN_PROGRESS.value],
                          'pending_jobs':
                              jobs[models.PrintJobState.PENDING.value],
                          'completed_jobs':
                              jobs[models.PrintJobState.DONE.value],
                          'worker_name':
                              worker_name,
                      })


class DraftJobQueue(_PrintJobQueueView):
    print_job_model_cls = models.DraftPrintJob
    template_file = 'draft_queue.html'


class FinalJobQueue(_PrintJobQueueView):
    print_job_model_cls = models.FinalPrintJob
    template_file = 'final_queue.html'


class _PrintJobPickUpView(View):

    print_job_model_cls = None

    def post(self, request, job_id):
        assert self.print_job_model_cls is not None

        worker_name = request.POST.get('worker_name', '')
        if not worker_name:
            return HttpResponseBadRequest('Worker name must be non-empty.')

        if not queue.pick_up_print_job(
                print_job_model_cls=self.print_job_model_cls,
                job_id=job_id,
                worker_name=worker_name):
            return HttpResponseBadRequest(
                'Could not pick up job. Check log for more details.')

        http_referer = request.META.get('HTTP_REFERER')
        if http_referer:
            return redirect(http_referer)
        return HttpResponse('Ok!')


class DraftJobPickUp(_PrintJobPickUpView):
    print_job_model_cls = models.DraftPrintJob


class FinalJobPickUp(_PrintJobPickUpView):
    print_job_model_cls = models.FinalPrintJob


class _PrintJobMarkCompletionView(View):

    print_job_model_cls = None

    def post(self, request, job_id):
        assert self.print_job_model_cls is not None

        worker_name = request.POST.get('worker_name', '')

        if not worker_name:
            return HttpResponseBadRequest('Worker name must be non-empty.')

        if not queue.mark_print_job_complete(
                print_job_model_cls=self.print_job_model_cls,
                job_id=job_id,
                worker_name=worker_name):
            return HttpResponseBadRequest(
                'Could not mark job as complete. Check log for more details.')

        http_referer = request.META.get('HTTP_REFERER')
        if http_referer:
            return redirect(http_referer)
        return HttpResponse('Ok!')


class DraftJobMarkCompletion(_PrintJobMarkCompletionView):
    print_job_model_cls = models.DraftPrintJob


class FinalJobMarkCompletion(_PrintJobMarkCompletionView):
    print_job_model_cls = models.FinalPrintJob


def _try_parse_int(s, default=None):
    try:
        return int(s)
    except ValueError:
        return default
