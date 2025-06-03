from flask import Flask 

def init_app(app: Flask):
    from commands import (
        upgrade_db
    )

    cmds_to_register = [
        upgrade_db
    ]

    for cmd in cmds_to_register:
        app.cli.add_command(cmd)