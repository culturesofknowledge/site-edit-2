# -*- coding: utf-8 -*-
"""
Tweaker - Database manipulation tool for CofK/EMLO.
Uses SQLAlchemy Core for database operations.

Usage:
    # Standalone
    from tweaker import DatabaseTweaker
    dt = DatabaseTweaker.from_django_settings()  # Uses Django settings
    dt = DatabaseTweaker.tweaker_from_connection(dbname, host, port, user, password)
    dt = DatabaseTweaker("postgresql://user:pass@host:5432/dbname")  # Direct URL

    # Console
    python -m tweaker --shell
    python -m tweaker --url postgresql://user:pass@host:5432/dbname --shell
"""

from tweaker.tweaker import DatabaseTweaker, TweakerError, DuplicateRelationshipError, InvalidRelationshipTypeError

__all__ = ['DatabaseTweaker', 'TweakerError', 'DuplicateRelationshipError', 'InvalidRelationshipTypeError']
__version__ = '2.1.0'  # SQLAlchemy version
