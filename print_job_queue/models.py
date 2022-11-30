from enum import Enum, unique

from django.conf import settings
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


class PrintJob(models.Model):
    STATE = (
        (member.value, name)
        for name, member in PrintJobState.__members__.items()
    )
    
    job_id = models.AutoField(primary_key=True)

    # See PrintJobState.
    state = models.IntegerField(choices=STATE)

    # The group which this job belongs to.
    group = models.CharField(max_length=25, blank=False, default='default_group')

    # The worker that is handling this job. Should be set when the job is in
    # either PROCESSING or DONE state.
    worker = models.CharField(max_length=25, blank=True)

    # The user who owns the printed documents. A user with a print job should
    # not be deleted. This is nullable for backwards compatibility.
    owner = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    # The country of the user that owns this job. Not a foreign key as users
    # can't change country anyway.
    owner_country = models.CharField(max_length=25,
                                     blank=True,
                                     default='Nowhere')

    class Meta:
        abstract = True

    @classmethod
    def make_pending(cls, owner, owner_country, group):
        return cls(state=PrintJobState.PENDING.value,
                   owner=owner,
                   owner_country=owner_country,
                   group=group)
    
    def __str__(self):
        return '{}'.format(self.job_id)


class PrintedDocument(models.Model):
    # Path to the document to print.
    file_path = models.FilePathField(match='*.pdf', recursive=True)

    # The number of times the document should be printed. Should be greater
    # than zero.
    print_count = models.PositiveIntegerField()

    class Meta:
        abstract = True


class DraftPrintJob(PrintJob):
    """Print job for draft translations.
    
    This is a separate table so job_id can be reused to distribute draft
    printing jobs in a round-robin fashion.
    """
    pass


class PrintedDraftDocument(PrintedDocument):
    # The print job that contains this document.
    job = models.ForeignKey(
        DraftPrintJob, on_delete=models.CASCADE, related_name='document_set')


class FinalPrintJob(PrintJob):
    """Print job for final translations.
    
    This is a separate table for the same reason DraftPrintJob is.
    """
    pass


class PrintedFinalDocument(PrintedDocument):
    # The print job that contains this document.
    job = models.ForeignKey(
        FinalPrintJob, on_delete=models.CASCADE, related_name='document_set')
