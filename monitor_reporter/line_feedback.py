import arrow
import peewee
from eyewitness.audience_id import AudienceId
from flask import Blueprint, request, current_app, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextSendMessage, TextMessage
from linebot.exceptions import (
    InvalidSignatureError
)

# TODO env variable for token
LINE_CHANNEL_ACCESS_TOKEN = ''
LINE_CHANNEL_SECRET = ''
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
bp = Blueprint('line_feedback', __name__, url_prefix='/line_feedback')
# annotation_pattern = re.compile("(\d+)\/(\d+)\/(\d+)\/(\d+)\/.*.jpg")


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
    arrive_timestamp = arrow.now().datetime
    if 'open the door' in content:
        # TODO register the audience
        audience_id = AudienceId(user_id=line_id, platform_id='line')
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
        # TODO pattern check and create feedback result
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content)
        )
