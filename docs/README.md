# Documentation

## Deployment

There are two methods:

1. Using Docker via the provided [docker-compose.yml](../docker-compose.yml) file.
2. Using Ansible via [IOI automation scripts](https://github.com/ioi/automation/tree/master/translation).

It is advised to add Nginx basic auth on top of the public URL.

IMPORTANT: Make sure all URLS under `/media/*` should NOT be publicly accessible without auth, as it contains the PDF files of the tasks.

The IOI automation scripts already take care of the above security concerns.


## Basic Concepts

There are three user accounts used for administering the system:

- `admin`: has full access to the Django admin interface.
- `ISC` (the International Scientific Committee): manages tasks and their primary English
  statements. ISC belongs to the `editor` group in Django, which can be given some rights
  to the Django admin interface.
- `staff`: monitors translations and handles printing.

There is also a translators' account for each combination of a country (a.k.a. team) and a language.
If a country translates to multiple languages, they should get multiple accounts.

A team consists of:

- One or more **leaders**, who will receive the team user account for task translation.
- Zero or more **on-site contestants**, who will receive printed task translations.
  For each contestant, the leaders pick the translation to print: it could be their
  their translation, somebody else's translation, or no translation.
- Zero or more **online contestants**, which will NOT receive printed task translations.

Before the start of a contest translation day, the admin creates a contest in the
system. Then, the ISC creates the tasks for the contest. For each task, ISC adds
the problem statement in English, and then they release the first version of the task.
After all tasks have been released, the admin marks the contest as public.
The teams then see the tasks and start translating.

During the translation session, the staff can monitor the translation status of all
the teams. On-site teams can also request to print their current translation for
a task, which will be monitored by staff as well.

When a team has finished translating a task, they can **finalize** their translation.
After all tasks are finalized, the team can **submit** the translations for printing.

The staff will see the submitted translations, print the translations accordingly
(one copy per language per task per on-site contestant). The team leaders then can
verify the translations and the staff can mark the translations as **sealed**.
This is the end of the translation session for the team.
Optionally, the team can opt out of the verification process when submitting.

Special rules apply when using somebody else's translation.
Consider a case when team A requested that one of their contestants receives
a translation by team B. Team A's translation may be submitted only if team B
already submitted their translation, or if team B promised to produce the
translation (by click the appropriate button on their home page).


## Initial setup

There are 3 administrator users: `admin`, `ISC`, and `staff`.
The IOI automation scripts will add those users. If Docker is used, the users will need to be added manually:

```
docker-compose exec app bash
```

and then:

```
python3 manage.py loaddata initial_data.json
```

### Changing administrator user passwords

Initially, each of the administrator user's password is the same as the
username. For security reasons, we need to change the passwords of all the
three users. To do this, log in as `admin`, go to `Trans` -> `Users`, select
a user, and change the password using the provided form.

### Adding countries and languages

Default countries and languages data are provided at `data/countries.csv` and `data/languages.csv`. Modify them as necessary.

Then, log in as `admin`, go to `Trans` -> `Countries` -> `Import`, select the CSV file, choose the `csv` format, and click `Submit`.
Likewise for languages.

### Adding users

Similarly, we will import the users via a CSV file. Beware that Django administration lists two tables called `Users`.
You should use the one under "Trans", not under "Authentication and authorization".

See the default CSV file at `data/users.csv`. Modify the file as necessary. Here is the explanation of each column:

- `username`: the username, in most cases should be equal to the `country`.
- `raw_password`: the password (generate it).
- `country`: the 3-letter code country of this user.
- `language`: the language this user is translating into. Set as `en` if this user is not translating.
- `is_onsite`: `1` if the user is translating on-site, `0` otherwise

### Adding contestants

Finally, we should import contestants from a CSV file, see the defaults in `data/contestants.csv`.
Each contestant has the following columns:

- `user`: the name of the user who translates for this contestant (usually equal to the country code)
- `code`: the code of the contestant (e.g., `GHA1`).
- `name`: the full name of the contestant
- `on_site`: `1` if they are competing on-site, `0` otherwise
- `location`: an optional location in the contest hall (e.g., `H25`)

## Contest & Task Management

### Adding contests

To add a contest, log in as `admin`, go to `Trans` -> `Contests` -> `Add contest`.

The _slug_ is an alphanumeric identifier used in URLs.

The _public_ flag determines if the contest is visible to the translators.

If a contest is marked as _frozen_, its translation can no longer be edited.

### Adding tasks

To add a task, log in as `ISC`. Then, click the menu on the top-right corner, and select `Add New Task`.

The _name_ of the task is the alphanumeric codename used in the contest system.

### Writing task statements

ISC can start adding the task statement via the embedded editor.
The left pane is used for editing, the right one shows a preview.

The statements are written in Markdown (the [Marked.js dialect](https://marked.js.org/).
Mathematical expressions are supported using [KaTeX](https://katex.org/) syntax.

It is advisable to write each sentence in a separate line, to make it easier for the translators to track the translation.

To insert an image in the task statement, admin must first upload the image file as an attachment (`Trans` -> `Attachments`).
Then, the image can be added in the statement using this Markdown syntax: `![](hello_image1.png)`.

### Releasing ISC version

Once the statement of a task is final, ISC should release the first version.
This is done using the "Release" button in the editor.

### Making contests public

After the ISC has added all tasks of a contest, the admin can make the contest public by ticking the `Public` checkbox.
Once a contest is public, the translators will be able to see the latest released version of each task in the contest.

### Releasing further versions

Later, the ISC can decide to update the official statement and release
a new version. Each release comes with a release note visible to the translators.

## Monitoring Translations

### Viewing overall translation status

Upon login, the `staff` user will be presented with the translation status of all teams.

The User, Team, and Language columns are self-explanatory.

The Status column denotes the status of the overall translation:

- `In Progress`: the team has not submitted the translation yet.
- `Promised`: the team has not submitted the translation, but has promised to do so.
- `Waiting`: the translations have been submitted, but they cannot be printed yet,
  because some contestants are waiting for somebody else's promised translation.
- `Printing`: the translations have been submitted and they are now in the print queue.
  `(needs seal)` is added if manual verification and sealing is requested.
- `Done (sealed)`: the translation have been printed and sealed
  (sealed by the staff if the team opted out of verification).
- `Done (remote)`: the translations have been submitted and the team is off-site,
  so nothing else needs be done.

The last column contains status of the translation for each task:

- :page_facing_up: : shows a PDF file with a finalized translation.
- :heavy_minus_sign: : the team is not translating.
- :question: : there is no translation yet.
- :pencil2: : the team is still editing the translation.
- :heavy_multiplication_x: : the team decided not to translate this task.

### Updating translation status

Staff can click on each row in the User column, which will show the detailed translation
status status of that user (team).

Here, staff can:

- Force-freeze team's overall translation or individual task translations.
- Force-reopen (unfreeze) team's overall translation or individual task translations.
- Make or break promises on behalf of the team.
- View and edit the assignment of translations to contestants.
- Declare contestant envelopes (containing printed translations) sealed by the team, which will mark the translation as done.

### Showing public translation status

We can show the overall translation status to all teams in the translation room, by clicking the `Public View` in the menu.
It shows the same data as the staff's status page, but packed, so that it fits on a single large screen.

## Handling Printing Queues

For each contest, there are two printing **queues:**

- **draft** print jobs for a working version of a team's translation of a task.
  They can be requested by clicking a button in the edit interface.

- **final** print jobs for finalized translations.
  There will be (at most) one such print job per on-site team.
  If the `PRINT_BATCH_WHOLE_TEAM` setting is `False`, the job will consist of separate
  files for contestants.

If you want to use duplex printing, set `PRINT_BATCH_DUPLEX` to `True`
to make each task start at an odd page.

### Print workers

Each queue can be handled by one or more **workers,** set up in Django administration.
A worker represents one physical printer station, attended by a runner.

To distribute the load between available workers, you can give each worker _modulo_ and _index_
and it will receive jobs whose ID modulo _modulo_ is equal to _index_.

By default, printing is handled by the runners. A runner picks up a job by clicking a button,
opens the PDF files on their computer, and sends them to the printer.

Alternatively, a worker can have server-side printing enabled. Then the runner just clicks
a Print button, which invokes the `print.sh` script on the server. You are expected to customize
the script according to your printing setup.

When the job is printed, the runner marks the job as completed. Then they click on the team's
page to see if the team has requested verification. After verificaton (or if there is none),
they click the Seal button.

## Permissions

The translation system follows standard Django model of users, groups, and permissions.

Rights for editing the English original are given to members of the `editor` group,
normally containing only the `ISC` user. Beware that there still remain hard-wired references
to the user name within the code.

Rights for managing translations and printing are given to members of the `staff` group,
normally containing only the `staff` user. It could be useful to add `ISC` to this group,
so that the ISC will see the progress of translations.

The `trans.send_notifications` permission allows to send notifications to all users.
By default, it's allowed only to the administrator, but it could be useful to give
this permission to the `editor` or `staff` group.

The `trans.upload_translation_pdf` permission allows a staff member to upload
the final translation as a raw PDF file. This is meant as a work-around for cases when
the default formatting is found to be broken for a specific language or script.
By default, it's allowed only to the administrator, but giving it to the `staff` group
could be useful.

Another potentially useful change is granting permissions on the `Attachment` table
to the `editor` group. It enables the ISC to create/update/delete images and other
attachments to the task statement without having to ask the admin every time.

## Miscellaneous

- `<hr class=pagebreak>` in Markdown text forces a page break.

- `./manage.py export` can be used to export all Markdown sources, attachments, and
  generated PDFs as a directory tree.

- The `Flat pages` table contains HTML snippets that are inserted to the home page
  of normal users and the ISC.

- As an experimental feature, it is possible to embed the Markdown text of task
  stataments in the generated PDFs as embedded attachments. See the `EMBED_MARKDOWN`
  setting.

### Directory hierarchy

- `cache/CONTEST/TASK/TYPE/TASK-USER.pdf` is the rendered PDF, where `TYPE` is either `task`
  for a translation or `released` for the English original. Cached files may be deleted
  manually to force re-rendering; this is safe except when the user is in the middle of
  an operation.

- `media/draft/CONTEST/UUID.pdf` are draft print-outs. Files that are not in the draft
  print queue may be safely deleted.

- `media/final_pdf/CONTEST/TASK/LANGUAGE_COUNTRY.pdf` are the final versions
  (usually a copy of the cached PDF from the time when the translation of the task was
  last frozen).

- `media/batch/CONTEST/USER-CONTESTANT.pdf` and `media/batch/CONTEST/USER.pdf`
  are the final versions for printing. The former one is a batch of all translations
  for a given contestant. The latter one is for all contestants of the team
  (which one is produced depends on the `PRINT_BATCH_WHOLE_TEAM` setting.
