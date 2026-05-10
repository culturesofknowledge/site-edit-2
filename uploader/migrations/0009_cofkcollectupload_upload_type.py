from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0008_alter_cofkcollectupload_upload_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='cofkcollectupload',
            name='upload_type',
            field=models.CharField(default='work', max_length=20),
        ),
    ]
