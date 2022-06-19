import pathlib

from django.http import HttpResponse
from django.shortcuts import render

from print_job_queue import models, queue


def draft_queue(request):
    jobs = queue.query_all_draft_print_jobs()

    links = []
    for job in jobs:
        for document in job.document_set.all():
            path = pathlib.Path(document.file_path)
            links.append((path.name, document.print_count, job.owner.username))

    # TODO(raisfathin): Use template.
    link_html = lambda link: f'<a href="/draft_translations/{link[0]}">{link[0]} ({link[2]}; {link[1]})</a>'
    links_html = '\n'.join([f'<li>{link_html(link)}</li>' for link in links])

    return HttpResponse(f'<ul>{links_html}</ul>')


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
