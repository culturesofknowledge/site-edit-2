from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('core', '0002_initial'),
    ]
    operations = [


        # for db function uuid_generate_v4
        migrations.RunSQL(
            f'CREATE EXTENSION IF NOT EXISTS "uuid-ossp" ',
            f'DROP EXTENSION IF EXISTS "uuid-ossp" ',
        ),
    ]
