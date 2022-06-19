import pathlib

from django.http import HttpResponse
from django.shortcuts import render

from print_job_queue import queue


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
