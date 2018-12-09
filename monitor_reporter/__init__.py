import os

import flask_admin
from flask import Flask
from flask_admin.contrib.peewee import ModelView
from peewee import SqliteDatabase
from eyewitness.models.detection_models import (ImageInfo, DATABASE_PROXY, BboxDetectionResult)


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    db_obj = SqliteDatabase(os.path.join(app.instance_path, 'example.sqlite'))
    DATABASE_PROXY.initialize(db_obj)

    # actually we needn't set the db obj here, since we initialize proxy above
    app.config.from_mapping(
        # store the database obj in the instance folder
        DATABASE=db_obj,
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # apply the blueprints to the app
    from monitor_reporter import album, bar_chart
    app.register_blueprint(album.bp)
    app.register_blueprint(bar_chart.bp)

    # register flask-admin for ImageInfo, BboxDetectionResult
    admin = flask_admin.Admin(app, name='Example: Peewee')
    admin.add_view(ModelView(ImageInfo))
    admin.add_view(ModelView(BboxDetectionResult))

    return app
