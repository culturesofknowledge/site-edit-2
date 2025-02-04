from lib2to3.fixes.fix_input import context

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.contrib.auth.models import Group

from core import constant
from core.helper import perm_serv


class Command(BaseCommand):
    help = 'Adds groups and permissions for users'

    def handle(self, *args, **kwargs):

        group_permissions_dict = {
            # 'cofkviewer': [],
            # 'reviewer': [],
            constant.ROLE_EDITOR: [
                constant.PM_CHANGE_WORK,
                constant.PM_CHANGE_PERSON,
                constant.PM_CHANGE_PUBLICATION,
                constant.PM_CHANGE_LOCATION,
                constant.PM_CHANGE_INST,
                constant.PM_CHANGE_ROLECAT,
                constant.PM_CHANGE_LOOKUPCAT,
                constant.PM_CHANGE_SUBJECT,
                constant.PM_CHANGE_ORGTYPE,
                constant.PM_CHANGE_COLLECTWORK,
            ],
        }
        group_permissions_dict[constant.ROLE_SUPER] = group_permissions_dict[constant.ROLE_EDITOR] + [
            constant.PM_CHANGE_USER,
            constant.PM_CHANGE_COMMENT,
            constant.PM_VIEW_AUDIT,
            constant.PM_EXPORT_FILE_WORK,
            constant.PM_EXPORT_FILE_PERSON,
            constant.PM_EXPORT_FILE_LOCATION,
            constant.PM_EXPORT_FILE_INST,
            constant.PM_TRIGGER_EXPORTER,
        ]
        group_permissions_dict[constant.ROLE_CONTRIBUTING_EDITOR] = [
            constant.PM_CHANGE_WORK,
        ]

        # add permissions to groups
        for group_name, permission_codes in group_permissions_dict.items():
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Group '{group_name}' created."))

            for permission_code in permission_codes:
                permission = perm_serv.get_perm_by_full_name(permission_code)
                if permission:
                    group.permissions.add(permission)
                else:
                    self.stdout.write(self.style.ERROR(f'permission not found: {permission_code}'))

        # delete the cache so that newly created groups can be retrieved immediately
        cache.delete(constant.CACHE_GROUP_MAP_ID)
