from print_job_queue import models


def enqueue_draft_print_job(file_path, print_count, owner):
    job = models.DraftPrintJob.make_pending(owner=owner)
    job.save()
    doc = models.PrintedDraftDocument(job=job,
                                      file_path=file_path,
                                      print_count=print_count)
    doc.save()
    return job


def query_all_draft_print_jobs():
    return list(
        models.DraftPrintJob.objects.all().prefetch_related('document_set'))
