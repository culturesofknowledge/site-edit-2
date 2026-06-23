#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import django.utils.version as _v, traceback as _tb                                                                                                                                                      
_orig = _v.get_complete_version                           
def _watch(version=None):                                                                                                                                                                                
    if version is not None and len(version) != 5:         
        print(f'\n!!! BAD VERSION: {version!r}')                                                                                                                                                         
        _tb.print_stack(limit=20)
        raise RuntimeError(f'Bad version: {version!r}')                                                                                                                                                  
    return _orig(version)                                                                                                                                                                                
_v.get_complete_version = _watch



def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siteedit2.settings')
    # print('current DJANGO_SETTINGS_MODULE={}'.format(os.environ.get('DJANGO_SETTINGS_MODULE')))
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
