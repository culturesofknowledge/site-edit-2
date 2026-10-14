from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0014_alter_cofkunionwork_change_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cofkworkpersonmap',
            name='person_mentioned_inferred',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cofkworkpersonmap',
            name='person_mentioned_uncertain',
            field=models.SmallIntegerField(default=0),
        ),
    ]
