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


def pick_up_draft_job(job_id, worker_name):
    job = models.DraftPrintJob.objects.filter(job_id=job_id).first()
    if job is None:
        logger.warning(
            'worker `%s` attempted to pick up non-existent job with id %s',
            worker_name, job_id)
        return False
    if job.state != models.PrintJobState.PENDING.value:
        logger.warning(
            'worker `%s` attempted to pick up non-pending job with id %s',
            worker_name, job_id)
        return False

    job.state = models.PrintJobState.IN_PROGRESS.value
    job.worker = worker_name
    job.save()
    return True


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
