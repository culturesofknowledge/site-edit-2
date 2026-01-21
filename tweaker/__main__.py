#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Console entry point for tweaker.

Usage:
    # With Django settings
    python -m tweaker

    # Interactive Python shell with tweaker
    python -m tweaker --shell

    # Direct connection (without Django)
    python -m tweaker --host localhost --port 5432 --dbname emlo --user postgres --password secret
"""
import argparse
import os
import sys


def setup_django():
    """Setup Django environment."""
    # Add the project root to the path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siteedit2.settings')

    import django
    django.setup()


def main():
    parser = argparse.ArgumentParser(
        description='CofK/EMLO Database Tweaker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Start interactive shell with Django settings
    python -m tweaker --shell

    # Connect directly without Django
    python -m tweaker --shell --host localhost --dbname emlo --user postgres

    # Run a script file
    python -m tweaker --script my_tweaks.py
        """
    )

    parser.add_argument('--shell', '-s', action='store_true',
                        help='Start interactive Python shell with tweaker')
    parser.add_argument('--script', type=str,
                        help='Run a Python script with tweaker available')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Enable debug mode (print SQL)')

    # Direct connection options (bypass Django)
    conn_group = parser.add_argument_group('Direct connection (bypasses Django settings)')
    conn_group.add_argument('--host', type=str, help='Database host')
    conn_group.add_argument('--port', type=str, default='5432', help='Database port')
    conn_group.add_argument('--dbname', type=str, help='Database name')
    conn_group.add_argument('--user', type=str, help='Database user')
    conn_group.add_argument('--password', type=str, help='Database password')

    args = parser.parse_args()

    # Determine connection method
    use_direct_connection = all([args.host, args.dbname, args.user])

    if not use_direct_connection:
        # Setup Django for settings access
        setup_django()

    from tweaker import DatabaseTweaker

    # Create tweaker instance
    if use_direct_connection:
        password = args.password or os.environ.get('PGPASSWORD', '')
        dt = DatabaseTweaker.tweaker_from_connection(
            dbname=args.dbname,
            host=args.host,
            port=args.port,
            user=args.user,
            password=password,
            debug=args.debug
        )
        print(f"Connected to {args.dbname}@{args.host}:{args.port}")
    else:
        dt = DatabaseTweaker.from_django_settings(debug=args.debug)
        from django.conf import settings
        db = settings.DATABASES['default']
        print(f"Connected to {db['NAME']}@{db['HOST']} (via Django settings)")

    if args.script:
        # Run a script file
        with open(args.script) as f:
            script_code = f.read()
        exec(script_code, {'dt': dt, 'DatabaseTweaker': DatabaseTweaker})

    elif args.shell:
        # Start interactive shell
        try:
            from IPython import embed
            print("\nTweaker is available as 'dt'")
            print("Example: dt.get_work_from_iwork_id(12345)")
            embed(colors='neutral')
        except ImportError:
            import code
            print("\nTweaker is available as 'dt'")
            print("Example: dt.get_work_from_iwork_id(12345)")
            code.interact(local={'dt': dt, 'DatabaseTweaker': DatabaseTweaker})

    else:
        # Just print status and exit
        print("\nTweaker ready. Use --shell for interactive mode or --script to run a file.")
        print("\nQuick test - checking database connection...")
        if dt.database_ok():
            print("Database connection OK")
        else:
            print("Database connection FAILED")
            sys.exit(1)


if __name__ == '__main__':
    main()
