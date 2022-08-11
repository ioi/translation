from collections import defaultdict
import logging
import os

from django.db.models import Q

from trans import models

from print_job_queue import queue

logger = logging.getLogger(__name__)


def handle_user_contest_frozen_change(user_contest):
    """Manages the print job queue when the frozen status of user_contest changes.

    user_contest must be fully updated."""
    if user_contest.frozen:
        _enqueue_final_print_job_if_completed(user_contest)
        _enqueue_dependent_final_print_jobs_if_completed(user_contest)
    else:
        _invalidate_final_print_job(user_contest)
        # Dependent UserContests are intentionally kept as-is. This allows
        # pending dependent jobs to automatically pick up updated pdfs later.
        # It is important that merged pdfs never get removed.
        #
        # Potential inconsistencies should be resolved manually.


def _enqueue_final_print_job_if_completed(user_contest):
    assert user_contest.frozen

    if not user_contest.user.has_contestants():
        # There are no onsite contestants, no print job needs to be created.
        return

    if user_contest.final_print_job:
        # There is already a print job, no print job needs to be created.
        return

    file_paths_with_counts = defaultdict(int)

    def add_completed_dependency_pdf(contest_slug, extra_country_code, count):
        if not extra_country_code or not count:
            # Nothing to do.
            return True

        # There must be a user with the extra country code.
        user = models.User.objects.filter(
            country__code=extra_country_code).first()
        if user is None:
            return False
        language_code = user.language.code
        country_code2 = user.country.code2

        # There must be a UserContest as well with the corresponding
        # contest & extra country code.
        dependency = models.UserContest.objects.filter(
            contest__slug=contest_slug,
            user__country__code=extra_country_code).first()
        if not dependency or not dependency.frozen:
            return False

        merged_pdf_path = os.path.join(
            'media', 'merged', contest_slug,
            f'{user.language_code}-merged.pdf')
        if os.path.isfile(merged_pdf_path):
            file_paths_with_counts[merged_pdf_path] += count
        else:
            logger.warning(
                'Cannot find %s (supposedly complete) while processing user_contest %s %s',
                merged_pdf_path, user_contest.user, contest_slug)
        return True

    contest_slug = user_contest.contest.slug

    if not add_completed_dependency_pdf(contest_slug,
                                        user_contest.extra_country_1_code,
                                        user_contest.extra_country_1_count):
        return

    if not add_completed_dependency_pdf(contest_slug,
                                        user_contest.extra_country_2_code,
                                        user_contest.extra_country_2_count):
        return

    if not add_completed_dependency_pdf(contest_slug,
                                        user_contest.user.country.code,
                                        user_contest.user.num_of_contestants):
        return

    logger.info('enqueueing %s', file_paths_with_counts)
    user = user_contest.user
    user_contest.final_print_job = queue.enqueue_final_print_job(
        file_paths_with_counts=file_paths_with_counts,
        owner=user,
        owner_country=user.country.code,
        group=contest_slug)
    user_contest.save()


def _enqueue_dependent_final_print_jobs_if_completed(user_contest):
    contest_slug = user_contest.contest.slug
    country_code = user_contest.user.country.code
    dependents = models.UserContest.objects.filter(
        Q(contest__slug=contest_slug) &
        (Q(extra_country_1_code=country_code) |
         Q(extra_country_2_code=country_code))).exclude(id=user_contest.id)
    for dependent in dependents:
        _enqueue_final_print_job_if_completed(dependent)


def _invalidate_final_print_job(user_contest):
    assert not user_contest.frozen
    if user_contest.final_print_job:
        queue.invalidate_print_job(user_contest.final_print_job)
    user_contest.final_print_job = None
    user_contest.save()
