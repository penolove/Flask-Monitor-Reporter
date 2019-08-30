from datetime import datetime, timedelta

from flask import Blueprint, render_template, url_for
from eyewitness.models.detection_models import (ImageInfo, BboxDetectionResult)

bp = Blueprint('album', __name__, url_prefix='/album')


@bp.route('/<target>-<int:year>-<int:month>-<int:day>-<int:hour>')
def display_obj_drawn_images(target, year, month, day, hour):
    start_time = datetime(year, month, day, hour)
    end_time = start_time + timedelta(hours=1)
    drawn_images = set()

    query = BboxDetectionResult.select(BboxDetectionResult, ImageInfo).join(ImageInfo).where(
        BboxDetectionResult.label == target,
        ImageInfo.timestamp >= start_time,
        ImageInfo.timestamp <= end_time,)

    drawn_images |= set(
        i.image_id.drawn_image_path for i in query if i.image_id.drawn_image_path)

    img_list = [url_for('static', filename=i) for i in sorted(drawn_images)]
    return render_template('album.html', img_list=img_list, image_amount=len(img_list))
