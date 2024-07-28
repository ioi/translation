IOI Task Translation System
===========================

The IOI Task Translation System provides a web interface for translating the tasks (problems) into various languages during the International Olympiads in Informatics. The system was initially developed and first used in IOI 2017 in Tehran, Iran.

Work in progress
----------------

### Substantial changes

- Upgraded prehistoric version of Django to current 5.4.0.
  Among other things, this brings compatibility with recent Python.

- Changed how edit locks work – at the previous IOI, translators
  often had to wait for the lock to expire, because sending of AJAX
  requests on page close no longer works with modern browsers.
  We now use the Beacon API and we also make it possible to break
  the lock by force if needed.

- Implemented the new workflow from the winter meeting (see below).

- Support for off-site contestants made more explicit. Each team
  and each contestant now have an on-site flag.

- Fixed security issues – regular users were allowed to perform
  several privileged operations when they guessed the URL.

- All important actions are logged.

- Frozen contests are now properly read-only for both translators
  and staff.

- Handling of print jobs was simplified – both drafts and final
  tasks share the database model and vast majority of code now.

- Printing workers were made explicit. They are defined in the
  database together with rules for selection of jobs suitable for
  each worker.

- A worker can have printing enabled. Previously, staff just downloaded
  the final PDFs from the web and printed them manually. Now, staff can
  ask for a job be printed by the server. Still, the print-out has to be
  explicitly confirmed as done when it's collected at the printer.

- Duplex printing is supported. If enabled in the settings, task statements
  are padded by blank pages to an even number of pages.

### New workflow

- Each country [well, actually each account, since there can be multiple
  accounts for a country in case it translates to multiple languages]
  has a list of contestants.

- Team leaders choose a translation for each of their contestant.
  By default, it's their translation, but it can be somebody else's,
  or perhaps no translation.

- When a team leader want to finalize their translation, the system checks
  that all translations requested for their contestants are already frozen.

- Also, the team leader can opt out of verifying envelope contents.

- After finalization, a print job is generated. For each on-site contestant,
  it contains a batch with a banner sheet and the requested task translations.
  (Depending on configuration, the print job contains either one PDF per
  contestant or one PDF per country. The former can be more convenient
  as printers can separate files in their output bins; the latter can save
  time when printing manually.)

---

Features
--------

* Markdown editor with mathematical expressions support
* Support for right-to-left and southeastern languages
* Embedded printing system
* User-friendly editing environment with parallel view
* PDF generation with custom fonts
* Revision history with diff mode
* Handy notification system
* Full-featured admin page
* Support for multiple contests
* Dockerized and easy to develop and deploy


Documentation
-------------

Read the documentation [here](./docs/README.md).

Local Dev Setup
---------------

1. Install Docker and Docker Compose.
2. Clone the project to your machine.
3. Run `docker-compose up -d`.

At this point, the app will be running at `http://localhost:9000/`. You may optionally perform the following tasks:

* To create initial administrator users and groups, run `docker-compose exec app bash`, and then in the shell, run `python3 manage.py loaddata initial_data.json`. Then, exit from the shell by typing `exit`.
* To add countries, languages, and users, use the CSV importer in the admin interface. Sample data is provided in `data/`.
* You can get access to the system logs by running `docker-compose logs`. To follow the logs from now on, run `docker-compose logs -f --tail=0`.
* To stop the app, run `docker-compose stop`.

License
-------
This software is distributed under the MIT license,
and uses third party libraries that are distributed under their own terms
(see [LICENSE-3RD-PARTY.txt](./LICENSE-3RD-PARTY.txt)).

Copyright
---------
Copyright (c), IOI International Technical Committee.

Initiated by the IOI 2017 Host Technical Committee.
