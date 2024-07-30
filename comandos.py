# comandos.py
from slack_sdk.errors import SlackApiError
import time
from globals_manager import test_set_thread_ts, test_get_thread_ts

class SlackMenuHandler:
    def __init__(self):
        self.thread_id_menu = None

    def build_button_menu(self):
        button = {
            "type": "button",
            "text": {"type": "plain_text", "text": "Briefing"},
            "value": "!brief",
            "action_id": "button_1",
            "style": "primary"
        }

        description = "𝗕𝗿𝗶𝗲𝗳: Criador de briefing"

        return [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Olá, como posso te ajudar hoje? ✿*"}
            },
            {"type": "actions", "elements": [button]},
            {"type": "divider"},
            {
                "type": "context",
                "elements": [{"type": "plain_text", "text": description, "emoji": True}]
            }
        ]

    def post_menu(self, client, channel_id):
        try:
            result = client.chat_postMessage(
                channel=channel_id,
                text="Olá, como posso te ajudar hoje? ✿",
                blocks=self.build_button_menu()
            )
            if result["ok"]:
                self.thread_id_menu = result['ts']
            else:
                print("Failed to post menu message to thread.")
        except SlackApiError as e:
            print(f"Error posting message: {e}")

    def handle_button_click(self, ack, body, client):
        ack()
        action_id = body["actions"][0]["action_id"]
        if action_id == "button_1":
            self.start_briefing_process(client, body["channel"]["id"])

    def start_briefing_process(self, client, channel_id):
        try:
            response = client.chat_postMessage(
                channel=channel_id,
                text="Iniciando processo de criação de briefing. Como posso ajudar?"
            )
            if response["ok"]:
                new_thread_ts_briefing = response['ts']
                test_set_thread_ts(new_thread_ts_briefing)
                time.sleep(1)  # Consider removing this if not necessary
            else:
                print("Failed to post new thread message.")
        except SlackApiError as e:
            print(f"Error posting message: {e}")

# Initialize the handler
slack_menu_handler = SlackMenuHandler()

# Export functions to be used in the main application
def menu_comandos(client, channel_id):
    slack_menu_handler.post_menu(client, channel_id)

def handle_button_click(ack, body, client, context):
    slack_menu_handler.handle_button_click(ack, body, client)