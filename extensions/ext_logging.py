import logging 
import os 
import sys 
import uuid 
from logging.handlers import RotatingFileHandler

import flask 
from flask import Flask 

from configs import app_config 

def init_app(app: Flask):
    log_handlers: list[logging.Handler] = []
    log_file = app_config.LOG_FILE 

    if log_file:
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        log_handlers.append(
            RotatingFileHandler(
                filename=log_file,
                maxBytes=app_config.LOG_FILE_MAX_SIZE * 1024 * 1024,
                backupCount=app_config.LOG_FILE_BACKUP_COUNT,    
            )    
        )

    # Always add StreamHandler to log to console 
    sh = logging.StreamHandler(sys.stdout)
    log_handlers.append(sh)

    # Apply RequestIdFilter to log to console 
    for handler in log_handlers:
        handler.addFilter(RequestIdFilter())

    logging.basicConfig(
        level=app_config.LOG_LEVEL,
        format=app_config.LOG_FORMAT,
        datefmt=app_config.LOG_DATEFORMAT,
        handlers=log_handlers,
        force=True     
    )

    # Apply RequestIdFormatter to all handlers
    apply_request_id_formatter() 

    # Disable propagation for noisy loggers to avoid duplicate logs 
    logging.getLogger("sqlalchemy.engine").propagate = False 

    log_tz = app_config.LOG_TZ
    if log_tz:
        from datetime import datetime

        import pytz 

        timezone = pytz.timezone(log_tz)

        def time_converter(seconds):
            return datetime.fromtimestamp(seconds, tz=timezone).timetuple()
        
        for handler in logging.root.handlers:
            if handler.formatter:
                handler.formatter.converter = time_converter
    