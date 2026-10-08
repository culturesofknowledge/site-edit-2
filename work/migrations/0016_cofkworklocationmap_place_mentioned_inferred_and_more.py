from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0015_cofkworkpersonmap_person_mentioned_inferred_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cofkworklocationmap',
            name='place_mentioned_inferred',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cofkworklocationmap',
            name='place_mentioned_uncertain',
            field=models.SmallIntegerField(default=0),
        ),
    ]
