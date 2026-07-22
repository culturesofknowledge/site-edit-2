from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('suggestions', '0001_initial'),
        ('login', '0003_alter_cofkuser_username'),
    ]

    operations = [
        migrations.RunSQL(
            'ALTER TABLE cofk_union_suggestions ALTER COLUMN suggestion_author_id TYPE varchar(254)',
            'ALTER TABLE cofk_union_suggestions ALTER COLUMN suggestion_author_id TYPE varchar(30)',
        ),
    ]
