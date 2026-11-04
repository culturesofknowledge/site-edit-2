from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0016_cofkworklocationmap_place_mentioned_inferred_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cofkunionwork',
            name='accession_code',
            field=models.TextField(blank=True, null=True),
        ),
    ]
