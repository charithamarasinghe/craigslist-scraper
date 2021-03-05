from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from main import logger
from main import config


def get_slack_conversations():
    try:
        slack_token = config["SLACK"]["oauth_token"]
        client = WebClient(token=slack_token)
        response = client.conversations_list()
        conversations = response["channels"]
        return conversations
    except Exception as error:
        logger.error(str(error))


class SlackMsgSender:
    def __init__(self, channel, text):
        self.channel = channel
        self.text = text

    def get_slack_channel_id(self):
        conversations = get_slack_conversations()

        if len(conversations) > 0:
            channel_id = None
            for conversation in conversations:
                if conversation["name"] == self.channel:
                    channel_id = conversation["id"]

            return channel_id
        else:
            return None

    def create_slack_channel(self):
        try:
            slack_token = config["SLACK"]["oauth_token"]
            client = WebClient(token=slack_token)
            response = client.conversations_create(
                name=self.channel,
                is_private=False
            )
            channel_id = response["channel"]["id"]
            logger.info("channel created with id: {channel_id}".format(channel_id=channel_id))
            return channel_id
        except SlackApiError as e:
            logger.error(e.response["error"])

    def send_slack_msg(self):
        channel_id = self.get_slack_channel_id()
        if channel_id is None:
            channel_id = self.create_slack_channel()

        if channel_id is not None:
            try:
                slack_token = config["SLACK"]["oauth_token"]
                client = WebClient(token=slack_token)
                response = client.chat_postMessage(
                    channel=channel_id,
                    text=self.text
                )
                logger.info("message sending status code: {status_code}".format(status_code=response.status_code))
            except SlackApiError as e:
                logger.error(e.response["error"])
