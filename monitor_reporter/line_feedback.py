import re
import os

import arrow
import peewee
from eyewitness.audience_id import AudienceId
from eyewitness.config import (
    FEEDBACK_NO_OBJ,
    LINE_FALSE_ALERT_ANNOTATION_PATTERN,
    LINE_PLATFROM
)
from eyewitness.feedback_msg_utils import FeedbackMsg
from eyewitness.image_id import ImageId
from flask import Blueprint, request, current_app, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextSendMessage, TextMessage
from linebot.exceptions import (
    InvalidSignatureError
)


LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
bp = Blueprint('line_feedback', __name__, url_prefix='/line_feedback')
FALSE_ALERT_ANNOTATION_PATTERN = re.compile(LINE_FALSE_ALERT_ANNOTATION_PATTERN)


# TODO webhook for annotation
@bp.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    false_alter_feedback_handler = current_app.config['FALSE_ALTER_FEEDBACK_HANDLER']
    content = event.message.text
    line_id = event.source.user_id
    audience_id = AudienceId(user_id=line_id, platform_id=LINE_PLATFROM)
    arrive_timestamp = arrow.now().timestamp
    if 'open the door' in content:
        try:
            false_alter_feedback_handler.register_audience(
                audience_id, {'register_time': arrive_timestamp})
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="thank for your registration")
            )
        except peewee.IntegrityError:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="maybe you already registered")
            )
    else:
        matched_obj = FALSE_ALERT_ANNOTATION_PATTERN.match(content)
        # if false_alert feedback pattern matched
        if matched_obj is not None:
            false_alter_feedback_handler = current_app.config['FALSE_ALTER_FEEDBACK_HANDLER']
            feedback_dict = matched_obj.groupdict()
            image_id = ImageId(
                feedback_dict['channel'], feedback_dict['timestamp'], feedback_dict['file_format'])
            feedback_dict = {
                'audience_id': audience_id, 'receive_time': arrive_timestamp,
                'feedback_method': FEEDBACK_NO_OBJ, 'image_id': image_id,
                'feedback_meta': ''
            }
            # generate FeebackMsg obj
            feedback_obj = FeedbackMsg(feedback_dict)
            # insert into database
            false_alter_feedback_handler.handle(feedback_obj)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="annotation received: %s" % (str(image_id)))
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="No matched pattern")
            )
