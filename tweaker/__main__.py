#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Console entry point for tweaker (SQLAlchemy version).

Usage:
    # With Django settings
    python -m tweaker

    # Interactive Python shell with tweaker
    python -m tweaker --shell

    # Direct connection (without Django)
    python -m tweaker --host localhost --port 5432 --dbname emlo --user postgres --password secret

    # Using a connection URL
    python -m tweaker --url postgresql://user:pass@host:5432/dbname
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
        description='CofK/EMLO Database Tweaker (SQLAlchemy)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Start interactive shell with Django settings
    python -m tweaker --shell

    # Connect directly without Django
    python -m tweaker --shell --host localhost --dbname emlo --user postgres

    # Connect via URL
    python -m tweaker --shell --url postgresql://user:pass@localhost:5432/emlo

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
    conn_group.add_argument('--url', type=str,
                            help='SQLAlchemy connection URL (e.g., postgresql://user:pass@host:5432/db)')
    conn_group.add_argument('--host', type=str, help='Database host')
    conn_group.add_argument('--port', type=str, default='5432', help='Database port')
    conn_group.add_argument('--dbname', type=str, help='Database name')
    conn_group.add_argument('--user', type=str, help='Database user')
    conn_group.add_argument('--password', type=str, help='Database password')

    args = parser.parse_args()

    # Determine connection method
    use_url = args.url is not None
    use_direct_connection = all([args.host, args.dbname, args.user])

    if not use_url and not use_direct_connection:
        # Setup Django for settings access
        setup_django()

    from tweaker import DatabaseTweaker

    # Create tweaker instance
    if use_url:
        dt = DatabaseTweaker(args.url, debug=args.debug)
        print(f"Connected via URL (SQLAlchemy)")
    elif use_direct_connection:
        password = args.password or os.environ.get('PGPASSWORD', '')
        dt = DatabaseTweaker.tweaker_from_connection(
            dbname=args.dbname,
            host=args.host,
            port=args.port,
            user=args.user,
            password=password,
            debug=args.debug
        )
        print(f"Connected to {args.dbname}@{args.host}:{args.port} (SQLAlchemy)")
    else:
        dt = DatabaseTweaker.from_django_settings(debug=args.debug)
        from django.conf import settings
        db = settings.DATABASES['default']
        print(f"Connected to {db['NAME']}@{db['HOST']} (via Django settings, SQLAlchemy)")

    if args.script:
        # Run a script file
        with open(args.script) as f:
            script_code = f.read()
        exec(script_code, {'dt': dt, 'DatabaseTweaker': DatabaseTweaker})

    elif args.shell:
        # Start interactive shell
        try:
            from IPython import embed
            print("\nTweaker (SQLAlchemy) is available as 'dt'")
            print("Example: dt.get_work_from_iwork_id(12345)")
            print("Example: dt.execute_raw('SELECT count(*) FROM cofk_union_work')")
            embed(colors='neutral')
        except ImportError:
            import code
            print("\nTweaker (SQLAlchemy) is available as 'dt'")
            print("Example: dt.get_work_from_iwork_id(12345)")
            print("Example: dt.execute_raw('SELECT count(*) FROM cofk_union_work')")
            code.interact(local={'dt': dt, 'DatabaseTweaker': DatabaseTweaker})

    else:
        # Just print status and exit
        print("\nTweaker (SQLAlchemy) ready. Use --shell for interactive mode or --script to run a file.")
        print("\nQuick test - checking database connection...")
        if dt.database_ok():
            print("Database connection OK")
        else:
            print("Database connection FAILED")
            sys.exit(1)


if __name__ == '__main__':
    main()
