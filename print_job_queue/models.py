from enum import Enum, unique

from django.contrib.auth.models import User
from django.db import models


@unique
class PrintJobState(Enum):
    # The job has been created and is ready for pickup.
    PENDING = 0

    # The job is being processed by a worker.
    IN_PROGRESS = 1

    # The job has been processed by a worker. This is a terminal state.
    DONE = 2

    # The job has been invalidated. This is a terminal state.
    INVALID = 3

    # Like IN_PROGRESS, but sent to the printer automatically
    PRINTING = 4


@unique
class PrintJobType(Enum):
    DRAFT = 0
    FINAL = 1


STATE_CHOICES = [(item.value, item.name) for item in PrintJobState]
TYPE_CHOICES = [(item.value, item.name) for item in PrintJobType]

STATE_BY_VALUE = {item.value: item for item in PrintJobState}
TYPE_BY_VALUE = {item.value: item for item in PrintJobType}


class Worker(models.Model):
    name = models.CharField(max_length=255, blank=False, unique=True)

    # The worker handles only jobs of the given type.
    job_type = models.IntegerField(choices=TYPE_CHOICES, null=True)

    # If modulo is non-zero, the worker accepts only jobs for which
    # owner.id % modulo == index
    modulo = models.PositiveIntegerField(
        help_text="""
            If modulo is non-zero, this worker is restricted to jobs whose user ID
            is equal to index modulo the given number.
        """
    )
    index = models.PositiveIntegerField()

    # Can this worker print directly on the server?
    server_print = models.BooleanField(
        help_text="Allow printing on the server."
    )

    def __str__(self):
        return self.name


class PrintJob(models.Model):
    # See PrintJobState.
    state = models.IntegerField(choices=STATE_CHOICES)

    # The group which this job belongs to.
    # The translation system sets groups to contest slugs.
    group = models.CharField(max_length=25, blank=False)

    # See PrintJobType.
    job_type = models.IntegerField(choices=TYPE_CHOICES)

    # The worker that is handling this job. Should be set when the job is in
    # either IN_PROGRESS, PRINTING, or DONE state.
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT, blank=True, null=True)

    # The user who owns the printed documents. A user with a print job should
    # not be deleted. This is nullable for backwards compatibility.
    owner = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'Job #{self.id}'


class PrintedDocument(models.Model):
    # Print job that contains this document.
    job = models.ForeignKey(PrintJob, on_delete=models.CASCADE, related_name='document_set')

    # Path to the document to print.
    file_path = models.FilePathField(match='.*.pdf', recursive=True)

    # The number of times the document should be printed. Should be greater than zero.
    print_count = models.PositiveIntegerField()
