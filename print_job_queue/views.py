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


class DraftJobPickUp(View):

    def post(self, request, job_id):
        worker_name = request.POST.get('worker_name', '')
        if not worker_name:
            return HttpResponseBadRequest('Worker name must be non-empty.')

        if not queue.pick_up_draft_job(job_id=job_id, worker_name=worker_name):
            return HttpResponseBadRequest(
                'Could not pick up job. Check log for more details.')

        return redirect(reverse('draft_queue'))


def final_queue(request):
    jobs = queue.query_all_final_print_jobs()

    jobs_links = []
    for job in jobs:
        job_links = []
        for document in job.document_set.all():
            job_links.append((document.file_path, document.print_count))
        jobs_links.append((job_links, job.owner.username, job.state))

    # TODO(raisfathin): Use template.
    link_html = lambda link: f'<a href="/{link[0]}">{link[0]} x {link[1]}</a>'
    links_html = lambda links: '\n'.join(
        [f'<li>{link_html(link)}</li>' for link in links])
    job_links_html = lambda job: f'<ul>{links_html(job)}</ul>'
    jobs_links_html = '\n'.join([
        f'<li>Owner: {owner} ({models.PrintJobState(state)}) {job_links_html(job_links)}</li>'
        for (job_links, owner, state) in jobs_links
    ])

    return HttpResponse(f'<ul>{jobs_links_html}</ul>')
