IOI Translation System
======================

The IOI Translation System provides a web interface for translating the tasks (problems)
into various languages during the International Olympiads in Informatics.
The system has been developed and first used in the IOI 2017 in Tehran, Iran.

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


Deployment Steps
----------------

* Install [docker](https://docs.docker.com/engine/installation/) and
[docker-compose](https://docs.docker.com/compose/install/).
* You may create `docker-compose.override.yml` and change the variables such as db password.
* Run `docker-compose build`.
* Run `docker-compose create`.
* To start the system, just run `docker-compose start` and to stop it, run `docker-compose stop`.
* If you want to create essential data for the system (dbseed),
  run `docker-compose exec web bash` after the system has been started,
  then in the shell execute `python3 manage.py loaddata initial_data.json`
  for the very first time. This command will create essential users and groups.
  Then exit from the shell by typing `exit`.
* For creating sample data such as countries, languages or tasks,
  run `docker-compose exec web bash` after the system has been started,
  then in the shell execute `python3 manage.py initialize`.
  Then exit from the shell by typing `exit`.
* You may have access to the logs by running `dokcer-compose logs`,
  for following log from now on run `docker-compose logs -f --tail=0`.

Development Settings
--------------------

For using docker in development settings, please add `--reload` option
to the execution line of gunicorn in `docker-entrypoint.sh` file.
Then run docker by `docker-compose up --build`.

Screenshots
----------------
![Editing panel](https://raw.githubusercontent.com/ioi-2017/translation/master/docs/screenshots/edit.png)
See more screenshots [here](https://github.com/ioi-2017/translation/tree/master/docs/screenshots).

License
-------
This software is distributed under the MIT license,
and uses third party libraries that are distributed under their own terms
(see LICENSE-3RD-PARTY.txt).

Copyright
---------
Copyright (c) 2017, IOI 2017 Host Technical Committee
