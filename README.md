# IOI-Translation

The Translation Service web app. Desgined for IOI Competitions, used and testes on IOI 2017, Tehran, Iran.

Features
--------
* Markdown syntax with mathematical expression support
* Right-to-left and southeastern language support
* Dockerized and easy to develop and deploy
* User friendly editing environment (Live and Compareing mode)
* PDF generation with custom fonts
* Revision history with diff mode
* Supports countries with multiple languages
* ISC notification broadcast

Deployment Steps
----------------
* Install docker and docker-compose (You may find the installation guidline [https://docs.docker.com/engine/installation/](https://docs.docker.com/engine/installation/)
* You may create `docker-compose.override.yml` and change the variables such as db password
* Run `docker-compose build`
* Run `docker-compose create`
* To start the system, just run `docker-compose start` and to stop it, run `docker-compose stop`
* If you want to create essential data for the system (dbseed), run `docker-compose exec web bash` after the system has been started, then in the shell execute `python3 manage.py loaddata initial_data.json` for the very first time. This commmand will create essential users and groups. Then exit from the shell by typing `exit`.
* For creating sample data such as countries, languages or tasks, run `docker-compose exec web bash` after the system has been started, then in the shell execute `python3 manage.py initialize`. Then exit from the shell by typing `exit`.
* You may have access to the logs by running `dokcer-compose logs`, for following log from now on run `docker-compose logs -f --tail=0`

Development Settings
----------------
* For using docker in development settings, please add `--reload` option to the execution line of gunicorn in `docker-entrypoint.sh` file. Then run docker by `docker-compose up --build`.

Screenshots
----------------
![Editing panel](https://raw.githubusercontent.com/noidsirius/IOI-Translation/master/docs/screenshots/edit.png)


