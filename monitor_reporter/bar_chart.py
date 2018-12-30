import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict

from flask import Blueprint, render_template
from eyewitness.models.detection_models import (ImageInfo, BboxDetectionResult)

bp = Blueprint('bar_chart', __name__, url_prefix='/bar_chart')

valid_labels_env = os.environ.get('VALID_LABELS')
if valid_labels_env is None:
    valid_labels = set()
else:
    valid_labels = set(valid_labels_env.split(','))

@bp.route('/')
def index():
    channels = set(i.channel for i in ImageInfo.select())
    max_timestamp = max(i.timestamp for i in ImageInfo.select())
    # truncate the datetime obj
    start_time = max_timestamp.replace(minute=0, hour=0, second=0, microsecond=0)
    end_time = start_time + timedelta(days=1)
    result_tuples = generate_bar_chart_tuples(channels, start_time, end_time)
    return render_template('bar_chart.html', result_tuples=result_tuples)


@bp.route('/<int:year>-<int:month>-<int:day>')
def query_day_chart(year, month, day):
    channels = set(i.channel for i in ImageInfo.select())
    start_time = datetime(year, month, day)
    end_time = start_time + timedelta(days=1)
    result_tuples = generate_bar_chart_tuples(channels, start_time, end_time)
    return render_template('bar_chart.html', result_tuples=result_tuples)


def generate_bar_chart_tuples(channels, start_time, end_time):
    label_counter = defaultdict(list)
    for channel in channels:
        query = BboxDetectionResult.select().join(ImageInfo).where(
            ImageInfo.channel == channel,
            ImageInfo.timestamp >= start_time,
            ImageInfo.timestamp <= end_time,)

        for detected_object in query:
            # collect label appear time (minimum unit: hour)
            label = detected_object.label
            if valid_labels and label not in valid_labels:
                continue
            year = detected_object.image_id.timestamp.year
            month = detected_object.image_id.timestamp.month
            day = detected_object.image_id.timestamp.day
            hour = detected_object.image_id.timestamp.hour
            label_counter[label].append((year, month, day, hour))

    result_tuples = []
    for label, items in label_counter.items():
        time_counter = Counter(items)
        time_counter_str = create_time_counter_str(time_counter, label)
        result_tuples.append((label, time_counter_str))
    return result_tuples


def create_time_counter_str(time_counter, label):
    obj_list = []
    obj_template = "{ x: new Date(%s, %s, %s, %s), y: %s , cls: '%s'}"
    for date_tuple, count in time_counter.items():
        year, month, day, hour = date_tuple
        #  month need to minus 1 due to javascript start with 0
        obj_list.append(obj_template % (year, month - 1 , day, hour, count, label))
    return " , ".join(obj_list)
