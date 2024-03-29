# Generated by Django 4.0.6 on 2023-06-26 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0004_remove_cofkcollectplacementionedinwork_iwork_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cofkcollectinstitutionresource',
            name='institution_id',
        ),
        migrations.RemoveField(
            model_name='cofkcollectlocationresource',
            name='location_id',
        ),
        migrations.RemoveField(
            model_name='cofkcollectoccupationofperson',
            name='iperson_id',
        ),
        migrations.RemoveField(
            model_name='cofkcollectpersonresource',
            name='iperson_id',
        ),
        migrations.AddField(
            model_name='cofkcollectinstitutionresource',
            name='institution',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uploader.cofkcollectinstitution'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cofkcollectlocationresource',
            name='location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uploader.cofkcollectlocation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cofkcollectoccupationofperson',
            name='iperson',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uploader.cofkcollectperson'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cofkcollectpersonresource',
            name='iperson',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uploader.cofkcollectperson'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cofkcollectperson',
            name='iperson_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
