#! /bin/bash

# re-run with bash when started as `sh docker_fresh_setup.sh` (dash has no arrays)
if [ -z "$BASH_VERSION" ]; then
  exec bash "$0" "$@"
fi

#########
# Set up site-edit-2 in docker from scratch, following
# docs/running_site-edit-2_using_docker.md:
#
#  1. init git submodules, create .env / .db_old_env if missing
#  2. build images
#  3. start db and db_old
#  4. if the db container already has data: back it up to db_backups/ with
#     the current date and time, then drop and recreate the database
#  5. start web (runs migrate, createcachetable, add_groups_and_permissions)
#  6. restore the legacy pg dump into db_old (skipped if already restored)
#  7. run data_migration from db_old into db (takes hours, logged to logs/)
#  8. create a superuser (interactive)
#
# Run from the project home. data_migration takes ~5 hours, so run this
# inside tmux/screen or the migration dies with your terminal.
#
# usage: devscript/pg_data_dump_from_old.sh [--skip-build] --force-restore --dump db_dump/emlo-edit-db-dump-2023-03-24.gz [options]
#######

set -e
set -o pipefail

usage() {
  cat <<EOF
usage: $0 [options]

  --dump FILE              legacy pg dump (.sql or .gz) to restore into db_old
  --old-db-name NAME       database name in db_old (default: ouls)
  --force-restore          drop and re-restore the db_old database even if it already exists
  --keep-db                do not back up / reset the db container's database
  --skip-build             do not rebuild docker images
  --skip-data-migration    stop after the web container is up (no db_old restore or data_migration)
  --skip-superuser         do not prompt to create a superuser
  -y, --yes                do not ask for confirmation before resetting the database
  -h, --help               show this help
EOF
}

DUMP_FILE=""
OLD_DB_NAME="ouls"
FORCE_RESTORE=0
KEEP_DB=0
SKIP_BUILD=0
SKIP_DATA_MIGRATION=0
SKIP_SUPERUSER=0
ASSUME_YES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dump) DUMP_FILE="$2"; shift 2 ;;
    --old-db-name) OLD_DB_NAME="$2"; shift 2 ;;
    --force-restore) FORCE_RESTORE=1; shift ;;
    --keep-db) KEEP_DB=1; shift ;;
    --skip-build) SKIP_BUILD=1; shift ;;
    --skip-data-migration) SKIP_DATA_MIGRATION=1; shift ;;
    --skip-superuser) SKIP_SUPERUSER=1; shift ;;
    -y|--yes) ASSUME_YES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [ ! -f "manage.py" ]; then
  echo "Exit. this script should be run in project home."
  exit 99
fi

PROJECT_HOME="$(pwd)"
DOCKER_DIR="$PROJECT_HOME/docker/site-edit-2"
BACKUP_DIR="$PROJECT_HOME/db_backups"
DUMP_DIR="$PROJECT_HOME/db_dump"
LOG_DIR="$PROJECT_HOME/logs"
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"

log() { echo; echo "==> [$(date +%H:%M:%S)] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  die "docker compose is not installed"
fi
COMPOSE+=(-f "$DOCKER_DIR/docker-compose.yml" -f "$DOCKER_DIR/docker-compose-db-old.yml")
# note: with snap docker, redirect exec output through a pipe (`| cat > file`),
# writing straight to a file fails with "write /dev/stdout: bad file descriptor"
dc() { "${COMPOSE[@]}" "$@"; }

docker info >/dev/null 2>&1 || die "cannot talk to docker (is the daemon running and are you in the docker group?)"

# read KEY from an env file without sourcing it (values may contain $ and !)
env_val() {
  grep -E "^$1=" "$2" | tail -n1 | cut -d= -f2-
}

# wait until postgres in a service accepts TCP connections
# (the image's first-boot init server only listens on the unix socket)
wait_for_pg() {
  local service="$1" user="$2"
  for _ in $(seq 1 60); do
    if dc exec -T "$service" pg_isready -h localhost -U "$user" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  die "postgres in '$service' did not become ready"
}

# run a single SQL statement and print the bare result
pg_query() {
  local service="$1" user="$2" db="$3" sql="$4"
  dc exec -T "$service" psql -h localhost -U "$user" -d "$db" -tAc "$sql"
}

db_exists() {
  local service="$1" user="$2" db="$3"
  [ "$(pg_query "$service" "$user" postgres "SELECT 1 FROM pg_database WHERE datname = '$db'")" = "1" ]
}

table_count() {
  local service="$1" user="$2" db="$3"
  pg_query "$service" "$user" "$db" \
    "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema')"
}

#########
# 1. prerequisites
#########
log "Initialising git submodules"
git submodule update --init

if [ ! -f "$DOCKER_DIR/.env" ]; then
  log "Creating docker/site-edit-2/.env from env.example"
  cp "$DOCKER_DIR/env.example" "$DOCKER_DIR/.env"
fi
if [ ! -f "$DOCKER_DIR/.db_old_env" ]; then
  log "Creating docker/site-edit-2/.db_old_env"
  printf 'POSTGRES_USER=postgres\nPOSTGRES_PASSWORD=postgres\n' > "$DOCKER_DIR/.db_old_env"
fi

DB_USER="$(env_val POSTGRES_USER "$DOCKER_DIR/.env")"
DB_NAME="$(env_val POSTGRES_NAME "$DOCKER_DIR/.env")"
OLD_DB_USER="$(env_val POSTGRES_USER "$DOCKER_DIR/.db_old_env")"
OLD_DB_PASSWORD="$(env_val POSTGRES_PASSWORD "$DOCKER_DIR/.db_old_env")"
[ -n "$DB_USER" ] && [ -n "$DB_NAME" ] || die "POSTGRES_USER / POSTGRES_NAME missing in docker/site-edit-2/.env"

if [ "$SKIP_DATA_MIGRATION" = 0 ]; then
  [ -n "$DUMP_FILE" ] || die "--dump FILE is required (or pass --skip-data-migration)"
  [ -f "$DUMP_FILE" ] || die "dump file not found: $DUMP_FILE"
  # the dump must be inside db_dump/, which is mounted into db_old at /db_dump
  mkdir -p "$DUMP_DIR"
  DUMP_REAL="$(realpath "$DUMP_FILE")"
  if [ "$(dirname "$DUMP_REAL")" != "$(realpath "$DUMP_DIR")" ]; then
    log "Copying $DUMP_FILE into db_dump/"
    cp "$DUMP_REAL" "$DUMP_DIR/"
  fi
  DUMP_IN_CONTAINER="/db_dump/$(basename "$DUMP_REAL")"
fi

#########
# 2. build
#########
if [ "$SKIP_BUILD" = 0 ]; then
  log "Building images"
  dc build
fi

#########
# 3. databases
#########
log "Starting db and db_old"
DB_SERVICES=(db)
[ "$SKIP_DATA_MIGRATION" = 0 ] && DB_SERVICES+=(db_old)
dc up -d "${DB_SERVICES[@]}"
wait_for_pg db "$DB_USER"

#########
# 4. back up and reset existing data in db
#########
if [ "$KEEP_DB" = 0 ] && db_exists db "$DB_USER" "$DB_NAME"; then
  n_tables="$(table_count db "$DB_USER" "$DB_NAME")"
  if [ "$n_tables" -gt 0 ]; then
    log "Database '$DB_NAME' in db has $n_tables tables, backing it up"
    mkdir -p "$BACKUP_DIR"
    backup_file="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"
    dc exec -T db pg_dump -h localhost -U "$DB_USER" -Fc "$DB_NAME" | cat > "$backup_file" \
      || { rm -f "$backup_file"; die "pg_dump failed, database left untouched"; }
    [ -s "$backup_file" ] || die "backup file is empty, database left untouched"
    echo "Backup written to $backup_file ($(du -h "$backup_file" | cut -f1))"
    echo "Restore with: pg_restore -h localhost -p 25432 -U $DB_USER -d $DB_NAME --clean $backup_file"

    if [ "$ASSUME_YES" = 0 ]; then
      read -r -p "Drop and recreate database '$DB_NAME' in db? Type 'yes' to continue: " answer
      [ "$answer" = "yes" ] || die "aborted by user (backup kept)"
    fi

    log "Stopping web and django-q, recreating database '$DB_NAME'"
    dc stop web django-q
    pg_query db "$DB_USER" template1 "DROP DATABASE \"$DB_NAME\" WITH (FORCE)"
    pg_query db "$DB_USER" template1 "CREATE DATABASE \"$DB_NAME\""
  else
    log "Database '$DB_NAME' in db is empty, nothing to back up"
  fi
fi

#########
# 5. web: entrypoint runs makemigrations, migrate, createcachetable,
#    add_groups_and_permissions and then runserver
#########
log "Starting web (running migrations)"
dc up -d --force-recreate web
for _ in $(seq 1 180); do
  if dc logs web 2>/dev/null | grep -q "Starting server"; then
    break
  fi
  if [ -z "$(dc ps -q --status running web)" ]; then
    dc logs web | tail -n 50
    die "web container exited during start up"
  fi
  sleep 5
done
dc logs web 2>/dev/null | grep -q "Starting server" || die "web did not finish migrations in time, check: ${COMPOSE[*]} logs web"
log "Migrations done, starting django-q"
dc up -d --force-recreate django-q

#########
# 6. restore legacy dump into db_old
#########
if [ "$SKIP_DATA_MIGRATION" = 0 ]; then
  mkdir -p "$LOG_DIR"
  wait_for_pg db_old "$OLD_DB_USER"

  if db_exists db_old "$OLD_DB_USER" "$OLD_DB_NAME" && [ "$FORCE_RESTORE" = 1 ]; then
    log "Dropping existing '$OLD_DB_NAME' in db_old (--force-restore)"
    pg_query db_old "$OLD_DB_USER" postgres "DROP DATABASE \"$OLD_DB_NAME\" WITH (FORCE)"
  fi

  # the restored dump's file name is stored as a comment on the database,
  # so a re-run only skips the restore when the same dump is already loaded
  restore_marker="restored from $(basename "$DUMP_REAL")"
  if db_exists db_old "$OLD_DB_USER" "$OLD_DB_NAME" \
      && [ "$(table_count db_old "$OLD_DB_USER" "$OLD_DB_NAME")" -gt 0 ]; then
    current_marker="$(pg_query db_old "$OLD_DB_USER" postgres \
      "SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname = '$OLD_DB_NAME'")"
    if [ "$current_marker" = "$restore_marker" ]; then
      log "'$OLD_DB_NAME' in db_old is already $restore_marker, skipping restore (use --force-restore to redo)"
    else
      die "'$OLD_DB_NAME' in db_old already has data that was not ${restore_marker}" \
        "(it is: ${current_marker:-unknown}). Re-run with --force-restore to replace it."
    fi
  else
    case "$DUMP_IN_CONTAINER" in
      *.gz) reader="gunzip -c" ;;
      *) reader="cat" ;;
    esac
    # a pg_dumpall file creates its own databases and \connects to them,
    # a single-database dump needs the target database created first
    dump_head="$($reader "$DUMP_REAL" 2>/dev/null | head -n 5 || true)"
    if echo "$dump_head" | grep -q "database cluster dump"; then
      restore_db="postgres"
    else
      restore_db="$OLD_DB_NAME"
      db_exists db_old "$OLD_DB_USER" "$OLD_DB_NAME" \
        || dc exec -T db_old createdb -h localhost -U "$OLD_DB_USER" "$OLD_DB_NAME"
    fi
    restore_log="$LOG_DIR/restore_db_old_${TIMESTAMP}.log"
    log "Restoring $DUMP_IN_CONTAINER into db_old (about 10 minutes), log: $restore_log"
    dc exec -T db_old sh -c \
      "$reader '$DUMP_IN_CONTAINER' | psql -q -h localhost -U '$OLD_DB_USER' -d '$restore_db'" \
      2>&1 | cat > "$restore_log" || echo "psql reported errors during restore, see $restore_log"
    db_exists db_old "$OLD_DB_USER" "$OLD_DB_NAME" \
      || die "database '$OLD_DB_NAME' not found in db_old after restore (wrong --old-db-name?), see $restore_log"
    pg_query db_old "$OLD_DB_USER" postgres "COMMENT ON DATABASE \"$OLD_DB_NAME\" IS '$restore_marker'"
  fi

#########
# 7. data migration
#########
  migration_log="$LOG_DIR/data_migration_${TIMESTAMP}.log"
  log "Running data_migration (takes hours), log: $migration_log"
  dc exec -T web python3 manage.py data_migration \
    -d "$OLD_DB_NAME" -u "$OLD_DB_USER" -p "$OLD_DB_PASSWORD" -o db_old -t 5432 \
    2>&1 | tee "$migration_log"
fi

#########
# 8. superuser
#########
if [ "$SKIP_SUPERUSER" = 0 ]; then
  if [ -t 0 ]; then
    log "Create a superuser"
    dc exec web python3 manage.py createsuperuser
  else
    echo "Not a terminal, skipping createsuperuser. Run: ${COMPOSE[*]} exec web python3 manage.py createsuperuser"
  fi
fi

log "Done. site-edit-2 is running at http://localhost:8000"
[ "$SKIP_DATA_MIGRATION" = 0 ] && echo "db_old is no longer needed, stop it with: ${COMPOSE[*]} stop db_old"
exit 0
