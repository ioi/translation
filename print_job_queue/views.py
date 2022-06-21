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


def draft_queue(request):
    jobs = defaultdict(list)
    for job in queue.query_all_draft_print_jobs():
        jobs[job.state].append({
            'id':
                job.job_id,
            'owner':
                job.owner.username,
            'documents': [(os.path.basename(document.file_path),
                           document.print_count)
                          for document in job.document_set.all()],
        })

    logger.info('jobs = %s', jobs)

    return render(
        request,
        'draft_queue.html',
        context={
            'in_progress_jobs': jobs[models.PrintJobState.IN_PROGRESS.value],
            'pending_jobs': jobs[models.PrintJobState.PENDING.value],
            'completed_jobs': jobs[models.PrintJobState.DONE.value],
        })


def final_queue(request):
    jobs = defaultdict(list)
    for job in queue.query_all_final_print_jobs():
        jobs[job.state].append({
            'id':
                job.job_id,
            'owner':
                job.owner.username,
            'documents': [(document.file_path, document.print_count)
                          for document in job.document_set.all()],
        })

    logger.info('jobs = %s', jobs)

    return render(
        request,
        'final_queue.html',
        context={
            'in_progress_jobs': jobs[models.PrintJobState.IN_PROGRESS.value],
            'pending_jobs': jobs[models.PrintJobState.PENDING.value],
            'completed_jobs': jobs[models.PrintJobState.DONE.value],
        })


class _PrintJobPickUpView(View):

    print_job_model_cls = None
    redirect_to = None

    def post(self, request, job_id):
        assert self.print_job_model_cls is not None
        assert self.redirect_to is not None

        worker_name = request.POST.get('worker_name', '')
        if not worker_name:
            return HttpResponseBadRequest('Worker name must be non-empty.')

        if not queue.pick_up_print_job(
                print_job_model_cls=self.print_job_model_cls,
                job_id=job_id,
                worker_name=worker_name):
            return HttpResponseBadRequest(
                'Could not pick up job. Check log for more details.')

        return redirect(reverse(self.redirect_to))


class DraftJobPickUp(_PrintJobPickUpView):
    print_job_model_cls = models.DraftPrintJob
    redirect_to = 'draft_queue'


class FinalJobPickUp(_PrintJobPickUpView):
    print_job_model_cls = models.FinalPrintJob
    redirect_to = 'final_queue'


class DraftJobMarkCompletion(View):

    def post(self, request, job_id):
        worker_name = request.POST.get('worker_name', '')

        if not worker_name:
            return HttpResponseBadRequest('Worker name must be non-empty.')

        if not queue.mark_draft_job_complete(job_id=job_id,
                                             worker_name=worker_name):
            return HttpResponseBadRequest(
                'Could not mark job as complete. Check log for more details.')

        return redirect(reverse('draft_queue'))
