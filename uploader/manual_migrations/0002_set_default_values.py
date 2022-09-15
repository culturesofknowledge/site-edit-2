from django.db import migrations

from core.helper import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('uploader', '0001_initial'),
    ]
    operations = [
        *migrations_utils.create_default_change_user_timestamp('cofk_union_audit_literal'),
        *migrations_utils.create_default_change_user_timestamp('cofk_union_audit_relationship'),
        *migrations_utils.create_default_empty('cofk_union_audit_relationship', [
            'left_id_value_new',
            'left_id_decode_new',
            'left_id_value_old',
            'left_id_decode_old',
            'relationship_decode_left_to_right',
            'relationship_decode_right_to_left',
            'right_id_value_new',
            'right_id_decode_new',
            'right_id_value_old',
            'right_id_decode_old',

        ])
    ]
