# Administrator Tasks

This document describes the day-to-day tasks an administrator (Supervisor) performs on EMLO Site Edit-2.
Each step that needs a command shows the exact command to run; replace the values in angle brackets (`<...>`) with
your own, and omit the parts in square brackets (`[...]`) if you do not need them. The full option reference is in
[Admin Managed Commands](admin_managed_commands.md), and server installation is covered in
[Deployment Procedure](deployment_procedure.md).

## Table of Contents

- [Before You Start](#before-you-start)
- [User Management](#user-management)
  - [Create the first superuser](#create-the-first-superuser)
  - [Create a test account](#create-a-test-account)
  - [Add a new user from the Users page](#add-a-new-user-from-the-users-page)
  - [Edit a user and change roles](#edit-a-user-and-change-roles)
  - [Reset a user's password](#reset-a-users-password)
  - [Deactivate a user](#deactivate-a-user)
  - [Delete a user on the Django admin page](#delete-a-user-on-the-django-admin-page)
  - [Set up groups and permissions](#set-up-groups-and-permissions)
- [Export](#export)
  - [Trigger an export from the dashboard](#trigger-an-export-from-the-dashboard)
  - [Run an export manually](#run-an-export-manually)
  - [Collect the export files](#collect-the-export-files)
- [Import (Upload and Review)](#import-upload-and-review)
  - [Upload a spreadsheet](#upload-a-spreadsheet)
  - [Review and accept or reject an upload](#review-and-accept-or-reject-an-upload)
  - [Troubleshooting an upload](#troubleshooting-an-upload)
- [Tweaker (Bulk Database Changes)](#tweaker-bulk-database-changes)
  - [Start the tweaker shell](#start-the-tweaker-shell)
  - [Run a tweak script](#run-a-tweak-script)
  - [Safety rules](#safety-rules)
- [Data Migration from the Old System](#data-migration-from-the-old-system)
- [Clearing Records](#clearing-records)
- [Routine Checks](#routine-checks)

---

## Before You Start

1. Know how the site is being run -- directly with `manage.py` on the host, or inside Docker. When the site runs in
   Docker, every management command in this document must be run inside the running web container instead of on the
   host. Either open a shell in the container first, or prefix the command with `docker exec`:
   
   ```bash
   # open a shell inside the web container (container name may differ in your environment)
   docker exec -it site-edit-2-web-1 /bin/bash
   # then run the commands below from /code
   
   # or run a single command without opening a shell
   docker exec -it site-edit-2-web-1 python3 /code/manage.py <command>
   ```
   
   On the host, run the commands from the project directory (the one containing `manage.py`), with the project's
   virtual environment activated. Add `--settings=siteedit2.settings.local_dev` to any `manage.py` command when you
   work on a local development environment.

2. Make sure you have the Superuser role in the application and, for the tasks under
   [Delete a user on the Django admin page](#delete-a-user-on-the-django-admin-page), a staff/superuser account for
   the Django admin site.

3. Make sure you can reach the server shell if a task needs a management command.

4. Take a database backup before any task that writes in bulk -- data migration, clearing records, tweaker scripts
   and accepting a large upload.

---

## User Management

Two different pages manage users, and they are not the same thing:

- **Users page** (`/user/search`, reachable from the dashboard) -- the normal place to create, edit, deactivate and
  reset passwords for editors. Requires the Supervisor role.
- **Django admin page** (`/admin/`) -- the low-level Django interface. It is the only place where a user can be
  **deleted** and where the superuser/staff flags can be changed. Requires a staff account.

The roles available in EMLO are: *Supervisor*, *Can edit Union and Bodleian card index catalogues* (Editor),
*Contributing Editor* and *Read-only access* (Viewer).

### Create the first superuser

Needed once per new deployment, when no account exists yet.

1. Open a shell on the server (or on the running web container).

2. Run Django's `createsuperuser` command:
   
   ```bash
   python3 manage.py createsuperuser
   ```

3. Enter the username, email and password when prompted. On a non-interactive deployment, pass the username and email
   as options and supply the password through the `DJANGO_SUPERUSER_PASSWORD` environment variable:
   
   ```bash
   python3 manage.py createsuperuser --username admin --forename Jane --surname Doe --email jane.doe@example.com
   
   # fully non-interactive
   DJANGO_SUPERUSER_PASSWORD='<password>' python3 manage.py createsuperuser --noinput \
       --username admin --forename Jane --surname Doe --email jane.doe@example.com
   ```

4. Log in to the site with the new account and confirm the dashboard shows the admin sections.

### Create a test account

Used on development and staging environments only.

1. Open a shell on the server (or container).

2. Run the `create_test_acc` command with a username and password, optionally an email address, and optionally the
   superuser switch if the account must also be a superuser/staff member:
   
   ```bash
   python3 manage.py create_test_acc -u <username> -p <password> [-e <email>] [-s]
   
   # example: a test supervisor account
   python3 manage.py create_test_acc -u tester -p 'Test1234' -e tester@example.com -s
   ```

3. Log in with the account to confirm it works, and remove it when the testing is finished.

### Add a new user from the Users page

1. Log in as a Supervisor.
2. On the dashboard, open **Users**.
3. Select **Add** to open the blank user form.
4. Fill in the email address, forename and surname. The email address becomes the username, so it must be unique and
   not longer than the username limit -- the form will tell you if it is too long.
5. Leave **Is active?** ticked so the person can log in.
6. Under **Roles**, tick the roles the person should have. Give the Supervisor role only to administrators.
7. Save the form.
8. Check the confirmation message at the top of the form. The system generates a password that nobody sees and emails
   the user a link to set their own. If the message says the email could not be sent, correct the email address and
   then use [Reset a user's password](#reset-a-users-password).

### Edit a user and change roles

1. Open **Users** from the dashboard.
2. Search by username, forename, surname, email or active status, and open the user from the results.
3. Change the name, email, active flag or roles as needed.
4. Save the form. Role changes take effect the next time the user loads a page.

### Reset a user's password

Administrators never see or set a user's password.

1. Open the user's record from the **Users** page.
2. Select **Reset password** and confirm.
3. A confirmation page tells you whether the email was sent. The user follows the emailed link to choose a new
   password.
4. If the email was not sent, check that the account has a valid email address and that the mail settings of the
   deployment are correct, then try again.

### Deactivate a user

Preferred over deletion, because it keeps the user's editing history intact.

1. Open the user's record from the **Users** page.
2. Untick **Is active?**.
3. Save. The account can no longer log in, and it can be re-enabled at any time by ticking the box again.

### Delete a user on the Django admin page

Delete only when the account was created in error and has no associated records. Deletion cannot be undone.

1. Confirm the account really has to be removed rather than deactivated.
2. Log in to `/admin/` with a staff account.
3. Open **Users** under the login section.
4. Search for the account by username, surname, forename or email.
5. Either open the record and use **Delete** at the bottom of the form, or tick the account in the list and choose the
   delete action from the action list.
6. Read the confirmation page carefully -- it lists every related object that will be removed with the user. Stop and
   deactivate the user instead if related records are listed.
7. Confirm the deletion and verify the account no longer appears on the **Users** page.

The same page is also where the **superuser** and **staff** flags are granted, which are required for access to the
Django admin site itself.

### Set up groups and permissions

Run after the first deployment, and again whenever the role definitions change in a release.

1. Open a shell on the server (or container).

2. Run the `add_groups_and_permissions` command. It creates the Editor, Supervisor and Contributing Editor groups and
   re-applies their permissions:
   
   ```bash
   python3 manage.py add_groups_and_permissions
   ```

3. Note that permissions of an existing group are cleared and re-assigned, so any manual permission tweaks made in the
   Django admin will be lost.

4. Log in as a user of each role and confirm the expected dashboard sections appear.

---

## Export

Exporting produces a set of CSV files of the whole dataset. It is a long-running job, so the dashboard schedules it
rather than running it immediately.

### Trigger an export from the dashboard

1. Log in as a Supervisor.
2. Scroll to the **Export** section of the dashboard.
3. Select **Export**. The export is queued and will run during the coming night.
4. The section then shows "Exporter is pending...". While this message is displayed, a further request is not needed
   and the button is hidden.
5. Check the dashboard the next day -- when the message is gone, the run has finished.
6. The scheduled background worker must be running for the job to start; if the message never clears, see
   [Routine Checks](#routine-checks).

### Run an export manually

Use when the files are needed immediately rather than overnight.

1. Open a shell on the server (or container).

2. Run the `exporter` command, choosing the output directory. Add the type option to choose between the standard flat
   CSV output and the Excel-style output, and add the skip-URL-check option if the run must not validate external
   links (this makes it much faster):
   
   ```bash
   python3 manage.py exporter [-o <output_dir>] [-t flat|excel] [-s]
   
   # export flat CSV files into /tmp/emlo_export without checking external URLs
   python3 manage.py exporter -o /tmp/emlo_export -t flat -s
   
   # same run inside Docker
   docker exec -it site-edit-2-web-1 python3 /code/manage.py exporter -o /tmp/emlo_export -t flat -s
   ```

3. Watch for errors in the output, and wait for the command to finish -- it can take a long time on a full dataset.

### Collect the export files

1. Look in the export output directory of the deployment (by default an `exporter` directory under the application
   home) for the generated CSV files.

2. Copy the files off the server. If the site runs in Docker, copy them out of the container first:
   
   ```bash
   # from the container to the host
   docker cp site-edit-2-web-1:/tmp/emlo_export ./emlo_export
   
   # from the server to your machine
   scp -r <user>@<server>:/tmp/emlo_export ./emlo_export
   ```

3. Confirm the file sizes and row counts look reasonable before passing them on.

---

## Import (Upload and Review)

Importing is a two-stage process: a spreadsheet is uploaded into a staging area, and nothing reaches the main
catalogue until an administrator reviews and accepts it.

### Upload a spreadsheet

1. Log in with an account that may work with uploads.
2. Open the upload section of the site (`/upload`).
3. Select **Add** to open the upload form.
4. Choose the catalogue the works belong to and select the spreadsheet file.
5. Submit the form. Large files are processed in the background: you are told the upload will continue after you leave
   the page, and an email is sent when it is done. Small files are processed immediately. The size threshold is a
   deployment setting.
6. Return to the upload list and check the new entry appears. Its status will be *Awaiting review*.

### Review and accept or reject an upload

1. Open the upload list. Only uploads that are *Awaiting review* or *Partly reviewed* are listed.
2. Open the upload you want to review. The header shows the status, the number of works uploaded, and how many have
   been accepted and rejected so far.
3. Work through each review area in turn:
   - **Works** -- the letters themselves.
   - **People** -- new people found in the spreadsheet.
   - **Locations** -- new places found in the spreadsheet.
   - **Corrections** -- changes the spreadsheet proposes to existing records.
4. In each area, check each row against the existing catalogue, especially for duplicates of people and locations that
   already exist in EMLO.
5. Accept the rows that should go into the main catalogue, or reject the ones that should not. Use **Accept all** or
   **Reject all** only when you have checked the whole list.
6. Confirm when prompted. Accepted items are written into the main catalogue and cannot be withdrawn from the review
   screen afterwards.
7. Repeat until nothing is left for review; the upload then leaves the pending list.

### Troubleshooting an upload

1. If an upload fails or stalls, reopen it from the upload list and read the reported errors.
2. Fix the spreadsheet -- most failures are missing mandatory columns, an unknown catalogue, or badly formatted dates
   -- and upload the corrected file as a new upload.
3. For a background (large file) upload that never completes, check that the background worker is running, as in
   [Routine Checks](#routine-checks).

---

## Tweaker (Bulk Database Changes)

The tweaker is a command-line tool for bulk corrections that are impractical through the web forms -- for example
retyping a relationship across hundreds of works. It writes directly to the database, so treat it as a last resort.

### Start the tweaker shell

1. Take a database backup first.

2. Open a shell on the server (or container), in the project directory.

3. Start the tweaker module with the shell option. By default it connects using the Django settings of the
   deployment; alternatively supply a database URL, or the host, port, database name, user and password separately:
   
   ```bash
   # use the Django settings of the deployment
   python3 -m tweaker --shell
   
   # connect through a database URL
   python3 -m tweaker --shell --url postgresql://<user>:<password>@<host>:5432/<dbname>
   
   # connect with separate connection options (password may also come from PGPASSWORD)
   python3 -m tweaker --shell --host localhost --port 5432 --dbname emlo --user postgres --password <password>
   
   # add --debug to print every SQL statement
   python3 -m tweaker --shell --debug
   ```

4. Confirm the connection details printed on start-up really point at the database you intend to change.

5. Use the tool's get, create, update and delete operations, then commit. Nothing is written until the change is
   committed, so you can abandon a session safely by leaving without committing.

### Run a tweak script

1. Prepare and review the tweak script, and have a second person check it when the change is large.

2. Run it first against a copy of the database or a staging environment.

3. Count the affected rows and compare them with what you expected.

4. Run the script on production with the tweaker's script option, then verify a sample of the changed records in the
   web interface:
   
   ```bash
   python3 -m tweaker --script <path/to/my_tweaks.py>
   
   # inside Docker
   docker exec -it site-edit-2-web-1 python3 -m tweaker --script /code/my_tweaks.py
   ```

### Safety rules

- Always back up before running the tweaker on production.
- Never run an unreviewed script.
- Prefer the typed relationship operations over raw SQL; the typed ones reject invalid relationship types and refuse
  to create duplicates.
- Make one logical change per run, so it is clear what to undo if something goes wrong.

---

## Data Migration from the Old System

Done once, when standing up a new instance from the old EMLO database.

1. Make sure the new database is empty and migrated to the current schema:
   
   ```bash
   python3 manage.py migrate
   python3 manage.py showmigrations
   ```

2. Obtain read access to the old Postgres database and note its name, host, port, user and password.

3. Open a shell on the server (or container).

4. Run the `data_migration` command with the connection details of the **old** database. Add the settings option if a
   non-default settings module must be used:
   
   ```bash
   python3 manage.py data_migration -d <db_name> -u <db_user> -p <db_password> -o <host> -t <port>
   
   # example against the old database on the host
   python3 manage.py data_migration -d ouls -u postgres -p password -o 172.17.0.1 -t 15432
   
   # example inside Docker, against the db_old container
   docker exec -it site-edit-2-web-1 python3 /code/manage.py data_migration -d ouls -u postgres -p postgres -o db_old -t 5432
   
   # with a non-default settings module
   python3 manage.py data_migration --settings=siteedit2.settings.local_dev -d ouls -u postgres -p password -o 172.17.0.1 -t 15432
   ```

5. Expect a long run; keep the output so any failures can be traced.

6. When it finishes, check record counts for works, people, locations and repositories against the old system, and
   spot-check a few records in the web interface.

7. Run `add_groups_and_permissions` and create the accounts, as described in [User Management](#user-management).

---

## Clearing Records

This destroys data. It is intended for development and for re-running a migration from scratch -- never for a live
catalogue.

1. Confirm the environment is not production.

2. Take a backup anyway.

3. Open a shell on the server (or container).

4. Run the `remove_all_records` command and answer the confirmation prompt (type `yes` to proceed):
   
   ```bash
   python3 manage.py remove_all_records
   ```

5. Verify the affected sections are empty, then reload or re-migrate the data.

---

## Routine Checks

- **Background worker** -- scheduled exports and large uploads rely on the background task service (Django-Q) of the
  deployment. If exports never finish or large uploads never complete, check that this service is running and read
  its log:
  
  ```bash
  # is the worker container up?
  docker compose -f docker/site-edit-2/docker-compose.yml ps
  
  # read its log
  docker compose -f docker/site-edit-2/docker-compose.yml logs -f django-q
  
  # start the worker manually (host or inside the web container)
  python3 manage.py qcluster
  ```

- **Email** -- password reset emails and upload notifications depend on the mail settings. After changing them, test
  by resetting the password of a test account.

- **Logs** -- check the application log for errors after any migration, large upload or tweaker run:
  
  ```bash
  tail -f emlo.log
  
  # inside Docker
  docker exec -it site-edit-2-web-1 tail -f /code/emlo.log
  ```

- **Backups** -- confirm that database backups run and can be restored, before any of the bulk tasks above.

- **Accounts** -- periodically review the user list and deactivate accounts that are no longer needed.
