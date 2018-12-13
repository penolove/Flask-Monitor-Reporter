import os

import flask_admin
from flask import Flask
from flask_admin.contrib.peewee import ModelView
from eyewitness.models import detection_models
from eyewitness.models import feedback_models
from eyewitness.models.db_proxy import DATABASE_PROXY
from eyewitness.result_handler.db_writer import FalseAlertPeeweeDbWriter
from peewee import SqliteDatabase


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    db_path = os.path.join(app.instance_path, 'example.sqlite')

    # which including build database obj
    database = SqliteDatabase(db_path)
    DATABASE_PROXY.initialize(database)
    false_alter_feedback_handler = FalseAlertPeeweeDbWriter(database)

    # actually we needn't set the db obj here, since we initialize proxy above
    app.config.from_mapping(
        DATABASE=database,
        FALSE_ALTER_FEEDBACK_HANDLER=false_alter_feedback_handler
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # apply the blueprints to the app
    from monitor_reporter import album, bar_chart, line_feedback
    app.register_blueprint(album.bp)
    app.register_blueprint(bar_chart.bp)
    app.register_blueprint(line_feedback.bp)

    # register flask-admin for ImageInfo, BboxDetectionResult,
    # RegisteredAudience, FalseAlertFeedback
    # create table if not exist
    detection_models.ImageInfo.create_table()
    detection_models.BboxDetectionResult.create_table()
    feedback_models.RegisteredAudience.create_table()
    feedback_models.FalseAlertFeedback.create_table()

    # register admin
    admin = flask_admin.Admin(app, name='Example: Peewee')
    admin.add_view(ModelView(detection_models.ImageInfo))
    admin.add_view(ModelView(detection_models.BboxDetectionResult))
    admin.add_view(ModelView(feedback_models.RegisteredAudience))
    admin.add_view(ModelView(feedback_models.FalseAlertFeedback))

    return app
