import re
import os

import arrow
import peewee
from eyewitness.audience_id import AudienceId
from eyewitness.config import (
    FEEDBACK_NO_OBJ,
    LINE_FALSE_ALERT_ANNOTATION_PATTERN,
    LINE_PLATFROM,
    LINE_FALSE_ALERT_MSG_TEMPLATE,
)
from eyewitness.feedback_msg_utils import FeedbackMsg
from eyewitness.image_id import ImageId
from flask import Blueprint, request, current_app, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    TextMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageAction,
)
from linebot.exceptions import (
    InvalidSignatureError
)

SITE_DOMAIN = os.environ.get('site_domain')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
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
    appier_image_id_mapping = current_app.config['APPIER_IMAGE_ID_MAPPING']
    content = event.message.text
    line_id = event.source.user_id
    audience_id = AudienceId(user_id=line_id, platform_id=LINE_PLATFROM)
    arrive_timestamp = arrow.now().timestamp
    if content in appier_image_id_mapping:
        try:
            false_alter_feedback_handler.register_audience(
                audience_id, {'register_time': arrive_timestamp})
        except peewee.IntegrityError:
            pass

        file_name, employ_name = appier_image_id_mapping[content]

        image_id = ImageId(channel=employ_name, timestamp=arrive_timestamp, file_format='jpg')
        false_alert_feedback_text = LINE_FALSE_ALERT_MSG_TEMPLATE.format(
            image_id=image_id, meta='I-want-to-be-a-member-of-183-Appier')
        image_url = '%s/%s'.format(SITE_DOMAIN, file_name)
        buttons_msg = TemplateSendMessage(
            alt_text='object detected',
            template=ButtonsTemplate(
                thumbnail_image_url=image_url,
                title='object detected',
                text='help to report result',
                actions=[
                    MessageAction(
                        label='Is This You?',
                        text=false_alert_feedback_text
                    ),
                ]
            )
        )
        line_bot_api.reply_message(
            event.reply_token,
            buttons_msg
        )
    else:
        matched_obj = FALSE_ALERT_ANNOTATION_PATTERN.match(content)
        # if false_alert feedback pattern matched
        if matched_obj is not None:
            false_alter_feedback_handler = current_app.config['FALSE_ALTER_FEEDBACK_HANDLER']
            feedback_dict = matched_obj.groupdict()
            image_id = ImageId(
                feedback_dict['channel'], feedback_dict['timestamp'], feedback_dict['file_format'])
            meta_data = feedback_dict.get('meta', '')
            is_false_alert = 'I-want-to-be-a-member-of-183-Appier' in meta_data
            feedback_dict = {
                'audience_id': audience_id, 'receive_time': arrive_timestamp,
                'feedback_method': FEEDBACK_NO_OBJ, 'image_id': image_id,
                'feedback_meta': meta_data, 'is_false_alert': is_false_alert,
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
