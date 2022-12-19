# Generated by Django 4.0.6 on 2022-12-19 10:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('institution', '0001_initial'),
        ('uploader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cofkinstitutionimagemap',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uploader.cofkunionimage'),
        ),
        migrations.AddField(
            model_name='cofkinstitutionimagemap',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='institution.cofkunioninstitution'),
        ),
        migrations.AddField(
            model_name='cofkcollectinstitutionresource',
            name='upload',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='uploader.cofkcollectupload'),
        ),
        migrations.AddField(
            model_name='cofkcollectinstitution',
            name='union_institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='institution.cofkunioninstitution'),
        ),
        migrations.AddField(
            model_name='cofkcollectinstitution',
            name='upload',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uploader.cofkcollectupload'),
        ),
        migrations.AlterUniqueTogether(
            name='cofkcollectinstitutionresource',
            unique_together={('upload', 'resource_id')},
        ),
        migrations.AlterUniqueTogether(
            name='cofkcollectinstitution',
            unique_together={('upload', 'institution_id')},
        ),
    ]
