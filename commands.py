import logging

import click 

@click.command("upgrade-db", help="Upgrade the database")
def upgrade_db():
    click.echo("Preparing database migration...")
    lock = redis_client.lock(name="db_upgrade_lock", timeout=60)
    if lock.acquire(blocking=False):
        try:
            click.echo(click.style("Starting database migration.", fg="green"))

            # run db migration 
            import flask_migrate 

            flask_migrate.upgrade() 

            click.echo(click.style("Database migration successful.", fg="green"))

        except Exception as e:
            logging.exception("Failed to execute database migration")
        
        finally: 
            lock.release()
    else:
        click.echo("Database migration skipped")