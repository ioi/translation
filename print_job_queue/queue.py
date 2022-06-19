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


def enqueue_final_print_job(file_paths_with_counts, owner):
    job = models.FinalPrintJob.make_pending(owner=owner)
    job.save()
    for file_path, count in file_paths_with_counts.items():
        doc = models.PrintedFinalDocument(job=job,
                                          file_path=file_path,
                                          print_count=count)
        doc.save()
    return job


def query_all_final_print_jobs():
    return list(
        models.FinalPrintJob.objects.all().prefetch_related('document_set'))


def invalidate_print_job(job):
    # TODO: What if the print job is already done?
    job.state = models.PrintJobState.INVALID.value
    job.save()
