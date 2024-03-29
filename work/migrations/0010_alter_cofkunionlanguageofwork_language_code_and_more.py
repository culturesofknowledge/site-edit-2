# Generated by Django 4.0.6 on 2023-06-15 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_cofkunionfavouritelanguage_language_code'),
        ('work', '0009_displayablework_alter_cofkunionwork_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cofkunionlanguageofwork',
            name='language_code',
            field=models.ForeignKey(db_column='language_code', on_delete=django.db.models.deletion.CASCADE, to='core.iso639languagecode'),
        ),
        migrations.AlterField(
            model_name='cofkunionlanguageofwork',
            name='work',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='language_set', to='work.cofkunionwork'),
        ),
    ]
