# Admin Managed Commands

This document provides information about custom Django management commands available in the EMLO project. These commands are primarily used for administration, data migration, and maintenance tasks.

## Table of Contents
- [Account Management](#account-management)
  - [create_test_acc](#create_test_acc)
- [Data Migration & Maintenance](#data-migration--maintenance)
  - [data_migration](#data_migration)
  - [remove_all_records](#remove_all_records)
  - [add_groups_and_permissions](#add_groups_and_permissions)
- [Data Export](#data-export)
  - [exporter](#exporter)

---

## Account Management

### `create_test_acc`
Creates a test user account with specified credentials and optional superuser status.

**Usage:**
```bash
python manage.py create_test_acc -u <username> -p <password> [-e <email>] [-s]
```

**Arguments:**
- `-u`, `--user`: (Required) Username for the new account.
- `-p`, `--password`: (Required) Password for the new account.
- `-e`, `--email`: (Optional) Email address for the user.
- `-s`, `--superuser`: (Optional) If provided, the user will be created as a superuser and staff member.

---

## Data Migration & Maintenance

### `data_migration`
Migrates data from an old EMLO database (Postgres) to the current system. This is a complex command typically used during initial setup.

**Usage:**
```bash
python manage.py data_migration -d <db_name> -u <username> -p <password> -o <host> -t <port>
```

**Arguments:**
- `-d`, `--database`: Name of the source database.
- `-u`, `--user`: Username for the source database.
- `-p`, `--password`: Password for the source database.
- `-o`, `--host`: Host address of the source database.
- `-t`, `--port`: Port number of the source database.

---

### `remove_all_records`
Deletes all data from several key tables in the database. Use with extreme caution.

**Usage:**
```bash
python manage.py remove_all_records
```

**Note:** This command will prompt for confirmation (`yes/NO`) before proceeding. It clears tables related to locations, persons, resources, and their mappings.

---

### `add_groups_and_permissions`
Initializes or resets the default groups (`Editor`, `Superuser`, `Contributing Editor`) and assigns them their respective permissions as defined in the code.

**Usage:**
```bash
python manage.py add_groups_and_permissions
```

**Note:** If a group already exists, its permissions will be cleared and re-assigned according to the current definitions in `constant.py` and `perm_serv.py`.

---

## Data Export

### `exporter`
Exports system data into CSV files.

**Usage:**
```bash
python manage.py exporter [-o <output_dir>] [-s] [-t <type>]
```

**Arguments:**
- `-o`, `--output-dir`: (Optional) Directory where export files will be saved. Defaults to current directory (`.`).
- `-s`, `--skip-url-check`: (Optional) Skip URL validation during export.
- `-t`, `--type`: (Optional) Type of export. 
  - `flat`: (Default) Standard CSV export.
  - `excel`: Excel-style CSV export.
