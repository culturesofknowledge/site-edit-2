from django.db import migrations

# some latitude/longitude values have leading or trailing whitespace (e.g. ' -0.1111', '54.02032\t'),
# which the exporter wrote as they are
TRIM_CHARS = r"E' \t\r\n '"


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0008_uuid_default'),
    ]

    operations = [
        migrations.RunSQL(f'''
            UPDATE cofk_union_location
            SET latitude  = btrim(latitude, {TRIM_CHARS}),
                longitude = btrim(longitude, {TRIM_CHARS})
            WHERE latitude <> btrim(latitude, {TRIM_CHARS})
               OR longitude <> btrim(longitude, {TRIM_CHARS})
        ''', migrations.RunSQL.noop),
    ]
