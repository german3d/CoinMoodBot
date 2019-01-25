import logging
from analytics.chatbase import Message
from config import CHATBASE_API_KEY


logging.basicConfig(format="%(asctime)s - %(name)s - {%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)

logger = logging.getLogger(__name__)



def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def send_chatbase_msg(intent, user_id, api_key=CHATBASE_API_KEY, version="1.0", platform="heroku"):
    chatbase_msg = Message(api_key=api_key,
                           platform=platform,
                           version=version,
                           intent=intent,
                           user_id=user_id,
                           message=intent)
    chatbase_resp = chatbase_msg.send();
    if chatbase_resp.status_code!=200:
        logger.warning("Error sending chatbase message with intent '{}', status code - '{}'"\
                        .format(intent, chatbase_resp.status_code))
