import logging
import subprocess

from django.db.models import F, Q

from print_job_queue import models

logger = logging.getLogger(__name__)


def enqueue_draft_print_job(file_path, print_count, group, owner, priority=0):
    job = models.PrintJob(state=models.PrintJobState.PENDING.value,
                          group=group,
                          job_type=models.PrintJobType.DRAFT.value,
                          owner=owner,
                          priority=priority)
    job.save()
    logger.info(f'Job #{job.id}: Enqueued draft job (priority={priority})')

    doc = models.PrintedDocument(job=job,
                                 file_path=file_path,
                                 print_count=print_count)
    doc.save()
    logger.info(f'Job #{job.id}: Added document {doc.file_path} copies={doc.print_count}')

    return job


def enqueue_final_print_job(file_paths_with_counts, group, owner, priority=0):
    job = models.PrintJob(state=models.PrintJobState.PENDING.value,
                          group=group,
                          job_type=models.PrintJobType.FINAL.value,
                          owner=owner,
                          priority=priority)
    job.save()
    logger.info(f'Job #{job.id}: Enqueued final job (priority={priority})')

    for file_path, count in file_paths_with_counts.items():
        doc = models.PrintedDocument(job=job,
                                     file_path=file_path,
                                     print_count=count)
        doc.save()
        logger.info(f'Job #{job.id}: Added document {doc.file_path} copies={doc.print_count}')

    return job


def invalidate_print_job(job):
    # TODO: What if the print job is already done?
    job.state = models.PrintJobState.INVALID.value
    job.save()
    logger.info(f'Job #{job.id}: Invalidated')


def query_group_print_jobs(group, job_type):
    return list(models.PrintJob.objects
                .filter(group=group, job_type=job_type.value)
                .prefetch_related('document_set')
                .order_by('create_time', '-priority'))


def query_worker_print_jobs(group, job_type, worker):
    query = (models.PrintJob.objects
             .filter(job_type=job_type.value, group=group))

    if worker.job_type is not None:
        query = query.filter(job_type=worker.job_type)

    if worker.modulo > 0:
        query = (query
                 .annotate(id_mod=F('owner_id') % worker.modulo)
                 .filter(Q(worker=worker) | Q(worker=None, id_mod=worker.index)))

    return list(
        query
        .prefetch_related('document_set')
        .order_by('create_time', '-priority'))


def print_on_server(worker, job):
    for doc in job.document_set.all():
        logger.info(f'Worker {worker.name}: Printing file {doc.file_path}')
        res = subprocess.run(['./print.sh', worker.name, doc.file_path])
        if res.returncode != 0:
            logger.error(f'Print script failed with return code {res.returncode}')
            raise RuntimeError('Print script failed')


def pick_up_print_job(job_id, worker, do_print=False):
    if not worker.server_print:
        do_print = False

    job = models.PrintJob.objects.filter(id=job_id).first()
    if job is None:
        logger.warning(f'Worker {worker.name}: Attempted to pick-up non-existent job #{job_id}')
        return None
    if job.state != models.PrintJobState.PENDING.value:
        logger.warning(f'Worker {worker.name}: Attempted to pick-up non-pending job #{job_id}')
        return None

    if do_print:
        job.state = models.PrintJobState.PRINTING.value
    else:
        job.state = models.PrintJobState.IN_PROGRESS.value
    job.worker = worker
    job.save()

    logger.info(f'Worker {worker.name}: Job {job.id} {"started printing" if do_print else "picked up"}')

    if do_print:
        print_on_server(worker, job)

    return job


def mark_print_job_complete(job_id, worker):
    job = models.PrintJob.objects.filter(id=job_id).first()
    if job is None:
        logger.warning(f'Worker {worker.name}: Attempted to complete non-existent job #{job_id}')
        return False
    if job.state not in (models.PrintJobState.IN_PROGRESS.value, models.PrintJobState.PRINTING.value):
        logger.warning(f'Worker {worker.name}: Attempted to complete non-in-progress job #{job_id}')
        return False
    if job.worker != worker:
        logger.warning(f"Worker {worker.name}: Attempted to complete another worker's job #{job_id}")
        return False

    job.state = models.PrintJobState.DONE.value
    job.save()

    logger.info(f'Worker {worker.name}: Job {job.id} completed')
    return True


def restart_print_job(job_id):
    job = models.PrintJob.objects.filter(id=job_id).first()
    if job is None:
        logger.warning(f'Attempted to restart non-existent job #{job_id}')
        return False

    job.state = models.PrintJobState.PENDING.value
    job.worker = None
    job.save()

    logger.info(f'Job {job.id}: Restarted')
    return True
