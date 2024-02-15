from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('person', '0001_initial'),
    ]
    operations = [
        migrations_utils.create_operation_seq('cofk_union_person_iperson_id_seq'),
    ]
