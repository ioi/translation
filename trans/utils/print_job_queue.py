import logging

from print_job_queue import queue

logger = logging.getLogger(__name__)


def handle_user_contest_frozen(user_contest, pdf):
    """Manages the print job queue when a user_contest is frozen with a new final PDF."""

    assert user_contest.frozen

    user = user_contest.user
    contest = user_contest.contest

    if not pdf:
        logger.info(f'No final PDF for {contest.slug}/{user.username}')
        return

    logger.info(f'Enqueueing {pdf} for {contest.slug}/{user.username}')

    user_contest.final_print_job = queue.enqueue_final_print_job(
        file_paths_with_counts={pdf: 1},
        owner=user,
        owner_country=user.country.code,
        group=contest.slug)
    user_contest.save()


def handle_user_contest_unfrozen(user_contest):
    """Manages the print job queue when a user_contest is un-frozen."""

    assert not user_contest.frozen

    if user_contest.final_print_job:
        queue.invalidate_print_job(user_contest.final_print_job)
        user_contest.final_print_job = None
        user_contest.save()
