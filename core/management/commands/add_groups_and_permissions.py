from lib2to3.fixes.fix_input import context

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.contrib.auth.models import Group

from core import constant
from core.helper import perm_serv


class Command(BaseCommand):
    help = 'Adds groups and permissions for users'

    def handle(self, *args, **kwargs):
        print('Adding groups and permissions...')

        group_permissions_dict = {
            # 'cofkviewer': [],
            # 'reviewer': [],
            constant.ROLE_EDITOR: [
                constant.PM_CHANGE_WORK,
                constant.PM_CHANGE_PERSON,
                constant.PM_CHANGE_PUBLICATION,
                constant.PM_CHANGE_LOCATION,
                constant.PM_CHANGE_INST,
                constant.PM_VIEW_ROLECAT,
                constant.PM_VIEW_SUBJECT,
                constant.PM_VIEW_ORGTYPE,
                constant.PM_CHANGE_LANGUAGE,
                constant.PM_ADD_SUGGESTIONS,
                constant.PM_VIEW_SUGGESTIONS,
                constant.PM_VIEW_AUDIT,
            ],
        }
        group_permissions_dict[constant.ROLE_SUPER] = group_permissions_dict[constant.ROLE_EDITOR] + [
            constant.PM_CHANGE_USER,
            constant.PM_CHANGE_COMMENT,
            constant.PM_EXPORT_FILE_WORK,
            constant.PM_EXPORT_FILE_PERSON,
            constant.PM_EXPORT_FILE_LOCATION,
            constant.PM_EXPORT_FILE_INST,
            constant.PM_TRIGGER_EXPORTER,
            constant.PM_CHANGE_COLLECTWORK,
            constant.PM_CHANGE_SUBJECT,
            constant.PM_CHANGE_ORGTYPE,
            constant.PM_CHANGE_ROLECAT,
            constant.PM_VIEW_LOOKUPCAT,
            constant.PM_CHANGE_LOOKUPCAT,
            constant.PM_VIEW_RESOURCE_DESC,
            constant.PM_CHANGE_RESOURCE_DESC,
        ]
        group_permissions_dict[constant.ROLE_CONTRIBUTING_EDITOR] = [
            constant.PM_CHANGE_WORK,
            constant.PM_VIEW_LOOKUPCAT,
            constant.PM_VIEW_SUGGESTIONS,
            constant.PM_CHANGE_SUGGESTIONS,
        ]

        print('Adding permissions to groups...')
        print('###################################')
        # add permissions to groups
        for group_name, permission_codes in group_permissions_dict.items():
            print(f'\nAdding permissions to group {group_name}...')
            print('***********************************************')
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                print(f'Group {group_name} created.')
                self.stdout.write(self.style.SUCCESS(f"Group '{group_name}' created."))
            else:
                # clear permissions for the group
                group.permissions.clear()

            for permission_code in permission_codes:
                permission = perm_serv.get_perm_by_full_name(permission_code)
                print(f'Adding permission {permission_code} to group {group_name}...')
                if permission:
                    group.permissions.add(permission)
                    self.stdout.write(self.style.SUCCESS(f"Permission '{permission_code}' added to group '{group_name}'."))
                else:
                    self.stdout.write(self.style.ERROR(f'permission not found: {permission_code}'))

        # delete the cache so that newly created groups can be retrieved immediately
        cache.delete(constant.CACHE_GROUP_MAP_ID)
        print('\nDone.')
