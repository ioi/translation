import logging

from django.db.models import F, Q

from print_job_queue import models

logger = logging.getLogger(__name__)


def enqueue_draft_print_job(file_path, print_count, owner, owner_country,
                            group):
    job = models.DraftPrintJob.make_pending(owner=owner,
                                            owner_country=owner_country,
                                            group=group)
    job.save()
    doc = models.PrintedDraftDocument(job=job,
                                      file_path=file_path,
                                      print_count=print_count)
    doc.save()
    return job


def query_worker_print_jobs(print_job_model_cls, group, worker_name, worker_mod,
                            worker_count):
    assert worker_name != '', 'Blank string is the default value used in the db.'

    # Fake comments so yapf can format the following statement nicely :(
    return list(
        print_job_model_cls.objects  #
        .filter(group=group)  #
        .prefetch_related('document_set')  #
        .annotate(job_mod=F('job_id') % worker_count)  #
        .filter(
            # Either a job that this worker has already claimed, completed job,
            # or an unclaimed job that is in the worker's queue based on the
            # worker's mod.
            Q(worker=worker_name) | Q(state=models.PrintJobState.DONE.value) |
            (Q(worker='') & Q(job_mod=worker_mod)))  #
        .order_by('job_id'))


def query_group_print_jobs(print_job_model_cls, group):
    # Fake comments so yapf can format the following statement nicely :(
    return list(print_job_model_cls.objects  #
                .filter(group=group)  #
                .prefetch_related('document_set')  #
                .order_by('job_id'))


def pick_up_print_job(print_job_model_cls, job_id, worker_name):
    job = print_job_model_cls.objects.filter(job_id=job_id).first()
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


def mark_print_job_complete(print_job_model_cls, job_id, worker_name):
    job = print_job_model_cls.objects.filter(job_id=job_id).first()
    if job is None:
        logger.warning(
            'worker `%s` attempted to complete non-existent job with id %s',
            worker_name, job_id)
        return False
    if job.state != models.PrintJobState.IN_PROGRESS.value:
        logger.warning(
            'worker `%s` attempted to complete non-in-progress job with id %s',
            worker_name, job_id)
        return False
    if job.worker != worker_name:
        logger.warning(
            'worker `%s` attempted to complete another worker\'s (`%s`) job with id %s',
            worker_name, job.worker, job_id)
        return False

    job.state = models.PrintJobState.DONE.value
    job.save()
    return True


def enqueue_final_print_job(file_paths_with_counts, owner, owner_country,
                            group):
    job = models.FinalPrintJob.make_pending(owner=owner,
                                            owner_country=owner_country,
                                            group=group)
    job.save()
    for file_path, count in file_paths_with_counts.items():
        doc = models.PrintedFinalDocument(job=job,
                                          file_path=file_path,
                                          print_count=count)
        doc.save()
    return job


def invalidate_print_job(job):
    # TODO: What if the print job is already done?
    job.state = models.PrintJobState.INVALID.value
    job.save()
