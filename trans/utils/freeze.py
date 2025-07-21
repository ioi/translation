# Freezing of UserContests

import logging

from django.db import transaction

from print_job_queue import queue

from trans.models import Translation, Contestant, Contest, User, UserContest, ContestantContest, Task
from trans.utils.batch import BatchRecipe

logger = logging.getLogger(__name__)


class UserContestFreezer:
    user: User
    contest: Contest
    tasks: list[Task]
    user_contest: UserContest
    dependencies: list[str]
    errors: list[str]
    _batch_recipe: BatchRecipe

    def __init__(self, user: User, contest: Contest):
        self.user = user
        self.contest = contest
        self.tasks = self.contest.task_set.order_by('order')
        self.user_contest, _ = UserContest.objects.get_or_create(contest=self.contest, user=self.user)
        self.dependencies = []
        self.errors = []
        self._batch_recipe = BatchRecipe(contest=self.contest, for_user=self.user, user_contest=self.user_contest)

    def check_own_translations(self):
        for task in self.tasks:
            trans = Translation.objects.filter(user=self.user, task=task).first()
            if not trans:
                self.errors.append(f'Task {task.name} has no translation')
            elif not trans.frozen:
                self.errors.append(f'Task {task.name} translation is not frozen')
            elif not trans.translating and self.user_contest.promised:
                self.errors.append(f'Task {task.name} is not translated, but you promised to translate it. Consult with staff, please.')

    def check_contestants(self) -> None:
        if not self.user.is_onsite:
            return

        for ctant in Contestant.objects.filter(user=self.user).order_by('code'):
            if not ctant.on_site:
                continue

            ct_recipe = self._batch_recipe.add_contestant(ctant)
            cc = ContestantContest.obtain(ctant, self.contest, self.user)
            by_user = cc.translation_by_user
            if by_user is not None:
                if by_user == self.user:
                    by_user_contest = self.user_contest
                else:
                    by_user_contest = UserContest.objects.filter(contest=self.contest, user=by_user).first()
                for task in self.tasks:
                    trans = Translation.objects.filter(user=by_user, task=task).first()
                    if by_user == self.user:
                        # The current user is either finalized or in the process of finalization,
                        # so if a task is not frozen, the user already got an error message.
                        pass
                    else:
                        if not trans:
                            err = 'which does not exist'
                        elif not trans.frozen or not by_user_contest or not by_user_contest.frozen:
                            err = 'which is not frozen yet'
                        else:
                            err = None
                        if err is not None:
                            msg = f'Contestant {ctant.code} requests translation of {task.name} to {by_user.language.name} ({by_user.country.name})'
                            if by_user_contest and by_user_contest.promised:
                                self.dependencies.append(f'{msg} {err}, but it is promised.')
                            else:
                                self.errors.append(f'{msg} {err}, ask the team for a promise.')
                    if trans and trans.translating:
                        ct_recipe.translations.append(trans)

    def freeze(self, by_user: User) -> None:
        logger.info(f'Freezing contest {self.contest.slug} for {self.user.username} by {by_user.username}')
        self.user_contest.frozen = True
        self.user_contest.save()

    def print_if_ready(self) -> None:
        if self.dependencies:
            for warn in self.dependencies:
                logger.info(f'Not ready: {warn}')
        else:
            pdfs = self._batch_recipe.build_pdfs()
            self.user_contest.ready = True
            if pdfs:
                logger.info(f'Enqueueing final PDFs for {self.contest.slug}/{self.user.username}: {" ".join(pdfs)}')
                self.user_contest.final_print_job = queue.enqueue_final_print_job(
                    file_paths_with_counts={pdf: 1 for pdf in pdfs},
                    owner=self.user,
                    group=self.contest.slug,
                    priority=0 if self.user_contest.skip_verification else 5)
                self.user_contest.sealed = False
            else:
                logger.info(f'No final PDFs for {self.contest.slug}/{self.user.username}')
                self.user_contest.sealed = False
            self.user_contest.save()

    def process_waiting(self) -> None:
        ccs = ContestantContest.objects.filter(contest=self.contest, translation_by_user=self.user).prefetch_related('contestant')
        users = set(cc.contestant.user for cc in ccs if cc.contestant.user != self.user and cc.contestant.user.is_onsite)
        for user in users:
            logger.info(f'Considering translation {user.username} dependent on {self.user.username}')
            with transaction.atomic():
                freezer = UserContestFreezer(user ,self.contest)
                if not freezer.user_contest.frozen:
                    logger.info('... not yet frozen')
                elif freezer.user_contest.ready:
                    logger.info('... already ready (how can this happen?)')
                else:
                    freezer.check_contestants()
                    assert not freezer.errors
                    freezer.print_if_ready()


def unfreeze_user_contest(user: User, contest: Contest, by_user: User) -> None:
    user_contest = UserContest.objects.filter(contest=contest, user=user).first()
    if user_contest is not None:
        logger.info(f'Unfreezing contest {contest.slug} for {user.username} by {by_user.username}')
        user_contest.frozen = False
        user_contest.ready = False
        user_contest.sealed = False
        if user_contest.final_print_job:
            queue.invalidate_print_job(user_contest.final_print_job)
            user_contest.final_print_job = None
        user_contest.save()
