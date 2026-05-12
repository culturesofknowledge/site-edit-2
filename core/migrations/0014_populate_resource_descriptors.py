from django.db import migrations


def populate_default_descriptors(apps, schema_editor):
    CofkResourceDescriptor = apps.get_model('core', 'CofkResourceDescriptor')

    default_descriptors = [
        # People descriptors
        ('CERL', 'People'),
        ('Deutsche Nationalbibliothek', 'People'),
        ('ODNB entry', 'People'),
        ('VIAF', 'People'),
        ('Wikidata ID', 'People'),
        ('Wikipedia', 'People'),
        # Places descriptors
        ('GeoNames', 'Places'),
        ('TGN', 'Places'),
        ('Wikidata ID', 'Places'),
        ('Wikipedia', 'Places'),
        # Repositories descriptors
        ('Online catalogue', 'Repositories'),
        ('Repository Homepage', 'Repositories'),
        ('Wikidata ID', 'Repositories'),
        ('Wikipedia', 'Repositories'),
        # Works descriptors
        ('Aubrey catalogue', 'Works'),
        ('Bodleian card catalogue', 'Works'),
        ('Comenius catalogue', 'Works'),
        ('Hartlib catalogue', 'Works'),
        ('Lhwyd catalogue', 'Works'),
        ('Lister catalogue', 'Works'),
        ('Oldenburg catalogue', 'Works'),
        ('Selden catalogue', 'Works'),
        ('Wallis catalogue', 'Works'),
        ('Wikidata ID', 'Works'),
        ('Wikipedia', 'Works'),
    ]

    for description, related_to in default_descriptors:
        CofkResourceDescriptor.objects.get_or_create(
            description=description,
            related_to=related_to,
        )


def reverse_populate(apps, schema_editor):
    CofkResourceDescriptor = apps.get_model('core', 'CofkResourceDescriptor')
    CofkResourceDescriptor.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_create_cofk_resource_descriptor'),
    ]

    operations = [
        migrations.RunPython(populate_default_descriptors, reverse_populate),
    ]
