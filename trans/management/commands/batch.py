from django.conf import settings
from django.core.management.base import BaseCommand
import sys

from trans.models import Contest, Task, User, Translation, UserContest
from trans.utils.batch import BatchRecipe, RecipeContestant


class Command(BaseCommand):
    help = "Prepares a batch PDF of all task statements and outputs its name"

    def add_arguments(self, parser):
        parser.add_argument("contest", help="Contest slug")

    def handle(self, *args, **options):
        contest = Contest.objects.filter(slug=options['contest']).first()
        if contest is None:
            print('No such contest', file=sys.stderr)
            sys.exit(1)

        user = User.objects.get(username="ISC")
        recipe = BatchRecipe(contest=contest, for_user=user, user_contest=None)
        ct_recipe = recipe.add_contestant(None)

        for task in Task.objects.filter(contest=contest).order_by('order'):
            trans = task.get_base_translation()
            if trans is None:
                print(f'Task {task.name} has no official translation')
            elif not trans.frozen:
                print(f'Task {task.name} official translation is not finalized')
            else:
                ct_recipe.translations.append(trans)

        out = recipe.build_pdfs()
        print(*out)
