# Running site-edit-2 using docker

## Build EMLO site-edit-2

```
git fetch
git checkout bugfix/docker_build_fix
git submodule update --init
docker compose -f docker/site-edit-2/docker-compose.yml build
docker compose -f docker/site-edit-2/docker-compose.yml up db db_old web
```

You will see errors in the web log but also that migrations have run

**NOTE:** The django-q container is likely still not working with docker and the qa branch is not working.

- Edit : django-q container works at this point

You can then login to the web container and see what migrations have run

```
docker exec -it site-edit-2-web-1 /bin/bash
python manage.py showmigrations
```

## Restore postgres data into db_old 

Once this is all working, you are ready to run the data migrations, for which we need the data in the  old_db

So, scp the pg dump file from cl-docker

```
scp cl-docker:~/emlo-edit-db-dump-2023-03-24.gz ./db_dump/
cd db_dump
gunzip emlo-edit-db-dump-2023-03-24.gz
mv emlo-edit-db-dump-2023-03-24 emlo-edit-db-dump-2023-03-24.sql
```
This file should be available within the db_old container, as the directory is shared as a volume

https://www.postgresql.org/docs/current/backup-dump.html#BACKUP-DUMP-RESTORE

You need to restore the data in `emlo-edit-pg-dump-test-2024-02-28.sql` to db_old
```
docker exec -it site-edit-2-db_old-1 /bin/bash
```
**NOTE** : The volume "db_dump" should be correctly mounted. The path used is relative to the location of the docker-compose file. So, the volumes command should actually be `../../db_dump/:/db_dump`. This is now fixed.

There should already be a database called `postgres` if not create one. Maybe called `ouls`

The command to restore dump is
```
# First create the database
createdb --username=postgres ouls

# Next restore the dump
psql --username=postgres --dbname=ouls < db_dump/emlo-edit-db-dump-2023-03-24.sql
```

Note: This took abotu 10 minutes on my machine

## Run migrations in web container, pointing to db_old

Do the migration of the data as in  the web page : https://github.com/culturesofknowledge/site-edit-2/tree/qa?tab=readme-ov-file#how-to-use-data-migration-tool

The password is obviously as in the [.db_old_env](https://github.com/culturesofknowledge/site-edit-2/blob/bugfix/docker_build_fix/docker/site-edit-2/.db_old_env) file.

```
python3 manage.py data_migration -d ouls -u postgres -p postgres -o db_old -t 5432
```

Ran well and finished successfully. Some minor errors that you can see below. It took almost 5 hours to complete.

```
$ docker exec -it site-edit-2-web-1 /bin/bash
# python3 manage.py data_migration -d ouls -u postgres -p postgres -o db_old -t 5432
<connection object at 0x70afb36d1f80; dsn: 'user=postgres password=xxx dbname=ouls host=db_old port=5432', closed: 0>
migrated records [     0s][    221][core.models.CofkLookupCatalogue]
migrated records [     0s][      7][core.models.CofkLookupDocumentType]
migrated records [     6s][  8,223][core.models.Iso639LanguageCode]
migrated records [     0s][      5][uploader.models.CofkCollectStatus]
migrated records [     0s][      3][core.models.CofkUnionOrgType]
migrated records [  3m,5s][189,960][core.models.CofkUnionResource]
migrated records [    53s][ 84,724][core.models.CofkUnionComment]
migrated records [    54s][ 68,260][core.models.CofkUnionImage]
migrated records [     0s][      1][core.models.CofkUnionSubject]
migrated records [     0s][     28][core.models.CofkUnionRoleCategory]
migrated records [     0s][    108][core.models.CofkUnionRelationshipType]
migrated records [     0s][     34][core.models.CofkUnionFavouriteLanguage]
migrated records [     1s][  1,129][uploader.models.CofkCollectUpload]
migrated records [     0s][    123][publication.models.CofkUnionPublication]
migrated records [     7s][  8,020][location.models.CofkUnionLocation]
migrated records [    43s][ 48,080][uploader.models.CofkCollectLocation]
migrated records [     0s][     56][uploader.models.CofkCollectLocationResource]
migrated records [  1m,0s][ 42,045][person.models.CofkUnionPerson]
migrated records [ 1m,56s][112,453][uploader.models.CofkCollectPerson]
migrated records [     0s][      6][uploader.models.CofkCollectOccupationOfPerson]
migrated records [     0s][    108][uploader.models.CofkCollectPersonResource]
migrated records [     0s][    554][institution.models.CofkUnionInstitution]
migrated records [     5s][  5,966][uploader.models.CofkCollectInstitution]
migrated records [     0s][     13][uploader.models.CofkCollectInstitutionResource]
migrated records [     0s][    158][login.models.CofkUser]
permission not found: core.trigger_exporter
migrated records [     1s][     -1][group & permission]
migrated records [     0s][    350][core.models.CofkUserSavedQuery]
migrated records [     0s][    106][core.models.CofkUserSavedQuerySelection]
migrated records [  6m,2s][204,089][work.models.CofkUnionWork]
migrated records [  3m,1s][167,073][work.models.CofkUnionLanguageOfWork]
migrated records [10m,16s][330,361][uploader.models.CofkCollectWork]
migrated records [21m,31s][332,705][uploader.models.CofkCollectAddresseeOfWork]
migrated records [19m,11s][334,260][uploader.models.CofkCollectAuthorOfWork]
migrated records [  1m,6s][ 16,350][uploader.models.CofkCollectDestinationOfWork]
migrated records [ 2m,11s][ 34,537][uploader.models.CofkCollectOriginOfWork]
migrated records [10m,33s][207,767][uploader.models.CofkCollectLanguageOfWork]
migrated records [ 3m,12s][ 37,785][uploader.models.CofkCollectPersonMentionedInWork]
migrated records [     0s][      1][uploader.models.CofkCollectSubjectOfWork]
migrated records [ 11m,6s][230,150][uploader.models.CofkCollectWorkResource]
migrated records [     4s][  1,537][uploader.models.CofkCollectPlaceMentionedInWork]
 created records [ 3m,33s][239,526][uploader.models.CofkCollectOriginOfWork]
 created records [ 2m,11s][154,463][uploader.models.CofkCollectDestinationOfWork]
migrated records [ 6m,45s][249,789][manifestation.models.CofkUnionManifestation]
migrated records [24m,56s][349,627][uploader.models.CofkCollectManifestation]
migrated records [     2s][  1,318][manifestation.models.CofkUnionLanguageOfManifestation]
migrated records [    25s][ 25,868][uploader.models.CofkCollectImageOfManif]
migrated records [     0s][      0][cofk_manif_comment_map]
migrated records [ 1m,21s][ 23,982][cofk_manif_comment_map]
migrated records [     0s][      0][cofk_manif_person_map]
migrated records [     0s][     38][cofk_manif_person_map]
migrated records [     1s][    161][cofk_manif_manif_map]
20250108 151920 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(233) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
20250108 152450 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(233) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
20250108 152450 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(233) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
20250108 152450 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(233) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
20250108 152450 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(233) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
20250108 152450 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(241) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
20250108 152451 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(246) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
20250108 152451 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(246) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
20250108 152451 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(246) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
20250108 152451 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(267) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
20250108 152451 WARN [MainThread] - insert or update on table "cofk_manif_inst_map" violates foreign key constraint "cofk_manif_inst_map_inst_id_35df6ef0_fk_cofk_unio" DETAIL:  Key (inst_id)=(267) is not present in table "cofk_union_institution".        --- [core.management.commands.data_migration--data_migration.insert_sql_val_list:178]
migrated records [14m,58s][155,997][cofk_manif_inst_map]
migrated records [     0s][      0][cofk_manif_inst_map]
migrated records [     0s][      0][cofk_manif_image_map]
migrated records [  7m,6s][ 68,210][cofk_manif_image_map]
migrated records [     4s][    617][cofk_person_location_map]
migrated records [     0s][      0][cofk_person_location_map]
migrated records [    22s][  3,312][cofk_person_person_map]
migrated records [     0s][      0][cofk_person_comment_map]
migrated records [    16s][  2,476][cofk_person_comment_map]
migrated records [ 3m,23s][ 33,038][cofk_person_resource_map]
migrated records [     0s][      0][cofk_person_resource_map]
migrated records [     0s][      0][cofk_person_image_map]
migrated records [     0s][      2][cofk_person_image_map]
migrated records [     4s][    642][cofk_person_role_map]
migrated records [     0s][      0][cofk_person_role_map]
migrated records [     0s][      0][cofk_work_comment_map]
migrated records [ 6m,19s][ 61,710][cofk_work_comment_map]
migrated records [14m,47s][144,746][cofk_work_resource_map]
migrated records [     0s][      0][cofk_work_resource_map]
migrated records [    38s][  5,795][cofk_work_work_map]
migrated records [     0s][      1][cofk_work_subject_map]
migrated records [     0s][      0][cofk_work_subject_map]
migrated records [24m,32s][236,353][cofk_work_person_map]
migrated records [21m,21s][201,556][cofk_work_person_map]
migrated records [23m,48s][229,107][cofk_work_location_map]
migrated records [     0s][      0][cofk_work_location_map]
migrated records [     4s][    697][cofk_institution_resource_map]
migrated records [     0s][      0][cofk_institution_resource_map]
migrated records [     0s][      0][cofk_institution_image_map]
migrated records [     0s][      0][cofk_institution_image_map]
migrated records [     0s][      0][cofk_location_comment_map]
migrated records [     4s][    632][cofk_location_comment_map]
migrated records [ 1m,12s][ 11,701][cofk_location_resource_map]
migrated records [     0s][      0][cofk_location_resource_map]
migrated records [     0s][      0][cofk_location_image_map]
migrated records [     0s][      0][cofk_location_image_map]
remove all audit records created by data_migrations
[END] remove all audit
total sec: 266m,59s
root@e8645f02a7de:/code# 

```

* Create admin user on the web container

```
$ docker exec -it site-edit-2-web-1 /bin/bash
root@e8645f02a7de:/code# python3 manage.py createsuperuser
Username: admin
Password: 
Password (again): 
The password is too similar to the username.
This password is too short. It must contain at least 8 characters.
This password is too common.
Bypass password validation and create user anyway? [y/N]: y
Superuser created successfully.
```

