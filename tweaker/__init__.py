# -*- coding: utf-8 -*-
"""
Tweaker - Database manipulation tool for CofK/EMLO.

Usage:
    # Standalone
    from tweaker import DatabaseTweaker
    dt = DatabaseTweaker.from_django_settings()  # Uses Django settings
    dt = DatabaseTweaker.tweaker_from_connection(dbname, host, port, user, password)

    # Console
    python -m tweaker
"""

from tweaker.tweaker import DatabaseTweaker

__all__ = ['DatabaseTweaker']
__version__ = '2.0.0'
