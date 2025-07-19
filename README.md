IOI Task Translation System
===========================

The IOI Task Translation System provides a web interface for translating the tasks (problems) into various languages during the International Olympiads in Informatics. The system was initially developed and first used in IOI 2017 in Tehran, Iran.


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
3. Run `docker compose up -d`.

At this point, the app will be running at `http://localhost:9000/`. You may optionally perform the following tasks:

* To create initial administrator users and groups, run `docker compose exec app bash`, and then in the shell, run `python3 manage.py loaddata initial_data.json`. Then, exit from the shell by typing `exit`.
* To add countries, languages, and users, use the CSV importer in the admin interface. Sample data is provided in `data/`.
* You can get access to the system logs by running `docker compose logs`. To follow the logs from now on, run `docker compose logs -f --tail=0`.
* To stop the app, run `docker compose stop`.

Creating a Service Account (Google Cloud Console) - Optional
-------
1. Go to **IAM & Admin → Service Accounts** in the Google Cloud Console.
2. Click **“Create Service Account”**.
3. Enter a **name** (e.g. `ioi-translation-bot`) and an optional description → **Create**.
4. Assign the single role: **Cloud Translation API User** (`roles/cloudtranslate.user`).
5. Click **Continue** and then **Done**.
6. Open the newly created service account in the list.
7. Go to the **Keys** tab → **Add Key → Create new key → JSON**.
8. Download the key file and save it as: `./secrets/google_service_account.json`.
10. Replace `CHANGE_ME_GCP_PROJECT_ID` in `docker-compose.yml` with your actual GCP project ID and start.

License
-------
This software is distributed under the MIT license,
and uses third party libraries that are distributed under their own terms
(see [LICENSE-3RD-PARTY.txt](./LICENSE-3RD-PARTY.txt)).

Copyright
---------
Copyright (c), IOI International Technical Committee.

Initiated by the IOI 2017 Host Technical Committee.
