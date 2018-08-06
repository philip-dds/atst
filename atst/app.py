import os
import re
import pathlib
from configparser import ConfigParser
from flask import Flask, request, g
from flask_session import Session
import redis
from unipath import Path
from flask_wtf.csrf import CSRFProtect

from atst.database import db
from atst.assets import environment as assets_environment

from atst.routes import bp
from atst.routes.workspaces import bp as workspace_routes
from atst.routes.requests import requests_bp
from atst.routes.dev import bp as dev_routes
from atst.domain.authnid.crl.validator import Validator
from atst.domain.auth import apply_authentication


ENV = os.getenv("FLASK_ENV", "dev")


def make_app(config):

    parent_dir = Path().parent

    app = Flask(
        __name__,
        template_folder=parent_dir.child("templates").absolute(),
        static_folder=parent_dir.child("static").absolute(),
    )
    redis = make_redis(config)
    csrf = CSRFProtect()

    app.config.update(config)
    app.config.update({"SESSION_REDIS": redis})

    make_flask_callbacks(app)
    make_crl_validator(app)

    db.init_app(app)
    csrf.init_app(app)
    Session(app)
    assets_environment.init_app(app)

    app.register_blueprint(bp)
    app.register_blueprint(workspace_routes)
    app.register_blueprint(requests_bp)
    if ENV != "production":
        app.register_blueprint(dev_routes)

    apply_authentication(app)

    return app


def make_flask_callbacks(app):
    @app.before_request
    def _set_globals():
        g.navigationContext = (
            "workspace"
            if re.match("\/workspaces\/[A-Za-z0-9]*", request.url)
            else "global"
        )
        g.dev = os.getenv("FLASK_ENV", "dev") == "dev"
        g.matchesPath = lambda href: re.match("^" + href, request.path)
        g.modalOpen = request.args.get("modal", False)
        g.current_user = {
            "id": "cce17030-4109-4719-b958-ed109dbb87c8",
            "first_name": "Amanda",
            "last_name": "Adamson",
            "atat_role": "default",
            "atat_permissions": [],
        }

    @app.template_filter('iconSvg')
    def _iconSvg(name):
        with open('static/icons/'+name+'.svg') as contents:
            return contents.read()


def map_config(config):
    return {
        "ENV": config["default"]["ENVIRONMENT"],
        "DEBUG": config["default"]["DEBUG"],
        "PORT": int(config["default"]["PORT"]),
        "SQLALCHEMY_DATABASE_URI": config["default"]["DATABASE_URI"],
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        **config["default"],
        "PERMANENT_SESSION_LIFETIME": int(config["default"]["PERMANENT_SESSION_LIFETIME"]),
    }


def make_config():
    BASE_CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), "../config/base.ini")
    ENV_CONFIG_FILENAME = os.path.join(
        os.path.dirname(__file__), "../config/", "{}.ini".format(ENV.lower())
    )
    OVERRIDE_CONFIG_FILENAME = os.getenv("OVERRIDE_CONFIG_FULLPATH")

    config = ConfigParser()
    config.optionxform = str

    config_files = [BASE_CONFIG_FILENAME, ENV_CONFIG_FILENAME]
    if OVERRIDE_CONFIG_FILENAME:
        config_files.append(OVERRIDE_CONFIG_FILENAME)

    config_files = [BASE_CONFIG_FILENAME, ENV_CONFIG_FILENAME]
    if OVERRIDE_CONFIG_FILENAME:
        config_files.append(OVERRIDE_CONFIG_FILENAME)

    # ENV_CONFIG will override values in BASE_CONFIG.
    config.read(config_files)

    # Assemble DATABASE_URI value
    database_uri = (
        "postgres://"
        + config.get("default", "PGUSER")
        + ":"
        + config.get("default", "PGPASSWORD")
        + "@"
        + config.get("default", "PGHOST")
        + ":"
        + config.get("default", "PGPORT")
        + "/"
        + config.get("default", "PGDATABASE")
    )
    config.set("default", "DATABASE_URI", database_uri)

    return map_config(config)

def make_redis(config):
    return redis.Redis.from_url(config['REDIS_URI'])

def make_crl_validator(app):
    crl_locations = []
    for filename in pathlib.Path(app.config["CRL_DIRECTORY"]).glob("*"):
        crl_locations.append(filename.absolute())
    app.crl_validator = Validator(
        roots=[app.config["CA_CHAIN"]], crl_locations=crl_locations
    )
    for e in app.crl_validator.errors:
        app.logger.error(e)

