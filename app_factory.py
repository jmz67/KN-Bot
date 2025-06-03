import logging 
import time 

from configs import app_config 
from flask import Flask 

from contexts.wrapper import RecyclableContextVar 

def create_flask_app_with_configs() -> Flask:
    """ 
    create a raw flask app 
    with configs loaded from .env file 
    """

    app = Flask(__name__)
    app.config.from_mapping(app_config.model_dump())

    @app.before_request
    def before_request():
        # add an unique indentifier to each request 
        RecyclableContextVar.increment_thread_recycles() 

    return app 

def create_app() -> Flask:
    start_time = time.perf_count() 
    app = create_flask_app_with_configs()

    initializa_extensions(app)
    end_time = time.perf_counter()

    if app_config.DEBUG:
        logging.info(f"Finished create_app ({round((end_time - start_time) * 1000, 2)} ms)")
    return app 

def initialize_extensions(app: Flask):
    from extensions import (
        ext_timezone, 
        ext_logging,
        ext_warnings,
        ext_import_modules,
        ext_app_metrics,
        ext_database,
        ext_migrate
    )

    extensions = [
        ext_timezone, 
        ext_logging,
        ext_warnings,
        ext_import_modules,
        ext_app_metrics,
        ext_database,
        ext_migrate    
    ]

    for ext in extensions:
        short_name = ext.__name__.split(".")[-1]
        is_enabled = ext.is_enabled() if hasattr(ext, "is_enabled") else True 
        if not is_enabled: 
            if app_config.DEBUG:
                logging.info(f"Skipped {short_name}")
            continue 

        start_time = time.perf_counter()
        ext.init_app(app) 
        end_time = time.perf_counter()
        if app_config.DEBUG:
            logging.info(f"Loaded {short_name} ({round((end_time - start_time) * 1000, 2)} ms)")

def create_migrations_app():
    app = create_flask_app_with_configs()
    from extensions import ext_database, ext_migrate 

    ext_database.init_app(app)
    ext_migrate.init_app(app) 

    return app 