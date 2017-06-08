import random, string
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from trans.models import Country, Language, User, Task, Contest
from trans.utils import get_trans_by_user_and_task


class Command(BaseCommand):
    help = 'Import initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            dest='reset',
            default=False,
            help='Remove previous data',
        )
        parser.add_argument(
            '--include', metavar='models', type=str, nargs='+',
            help='Select models to import',
            default=['countries', 'languages', 'translators', 'tasks']
        )

    def handle(self, *args, **options):
        reset = options['reset']
        for entry in options['include']:
            if entry == 'languages':
                self.import_languages('trans/initial_data/languages.csv', reset)
            if entry == 'countries':
                self.import_countries('trans/initial_data/countries.csv', reset)
            if entry == 'translators':
                self.import_translators('trans/initial_data/translators.csv', reset)
            if entry == 'tasks':
                self.import_tasks('trans/initial_data/tasks.csv', reset)

    def import_languages(self, file_name, reset):
        if reset:
            Language.objects.all().exclude(code='en').delete()

        with open(file_name, 'r') as file:
            file.readline()
            for line in file.readlines():
                name, code, direction = line.split(',')
                rtl = (direction.strip() == 'rtl')
                language, created = Language.objects.get_or_create(name=name.strip(), code=code.strip(), rtl=rtl)
                # print(name, code, direction=='rtl')

    def import_countries(self, file_name, reset):
        if reset:
            Country.objects.all().exclude(code='ISC').delete()

        with open(file_name, 'r') as file:
            file.readline()
            for line in file.readlines():
                name, code = line.split(',')
                country, created = Country.objects.get_or_create(name=name.strip(), code=code.strip())
                # print(name, code)

    def import_translators(self, file_name, reset):
        if reset:
            User.objects.filter(is_staff=False).all().delete()

        translator_group = Group.objects.get(name='translator')
        with open(file_name, 'r') as file:
            file.readline()
            for line in file.readlines():
                country_code, language_code = line.split(',')
                country_code = country_code.strip()
                language_code = language_code.strip()
                random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
                raw_password = "%s%s_%s" % (country_code, language_code, random_str)
                country = Country.objects.get(code=country_code.strip())
                language = Language.objects.get(code=language_code.strip())
                username = "%s_%s" % (language_code, country_code)
                user, created = User.objects.get_or_create(country=country, language=language, username=username)
                user.raw_password = raw_password
                user.set_password(raw_password)
                user.save()
                translator_group.user_set.add(user)
                # print(country, language, username, raw_password)

    def import_tasks(self, file_name, reset):
        if reset:
            Task.objects.all().delete()

        with open(file_name, 'r') as file:
            file.readline()
            for line in file.readlines():
                name, contest_slug = line.split(',')
                self.import_task("trans/initial_data/tasks/%s.md"%name, name.strip(), contest_slug.strip())

    def import_task(self, file_name, name, contest_slug):
        with open(file_name, 'r') as file:
            content = file.read()
            contest = Contest.objects.get(slug=contest_slug)
            task, created = Task.objects.get_or_create(name=name, contest=contest)
            user = User.objects.get(username="ISC")
            new_trans = get_trans_by_user_and_task(user, task)
            new_trans.add_version(content, "Init", True)