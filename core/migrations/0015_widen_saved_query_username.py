from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0014_populate_resource_descriptors'),
        ('login', '0003_alter_cofkuser_username'),
    ]

    operations = [
        migrations.RunSQL(
            'ALTER TABLE cofk_user_saved_queries ALTER COLUMN username TYPE varchar(254)',
            'ALTER TABLE cofk_user_saved_queries ALTER COLUMN username TYPE varchar(30)',
        ),
    ]
