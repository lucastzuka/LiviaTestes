# comandos.py
from slack_sdk.errors import SlackApiError
import time
from globals_manager import test_set_thread_ts, test_get_thread_ts

thread_id_menu = None

def build_button_menu():
    button_text = "Briefing"
    button_value = "!brief"
    button = {
        "type": "button",
        "text": {"type": "plain_text", "text": button_text},
        "value": button_value,
        "action_id": "button_1",
        "style": "primary"
    }

    description = """
    𝗕𝗿𝗶𝗲𝗳: Criador de briefing
    """

    sections = [
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
    return sections

def menu_comandos(client, channel_id):
    global thread_id_menu
    try:
        result = client.chat_postMessage(
            channel=channel_id,
            text="Olá, como posso te ajudar hoje? ✿",
            blocks=build_button_menu()
        )
        if result["ok"]:
            thread_id_menu = result['ts']
        else:
            print("Failed to post menu message to thread.")
    except SlackApiError as e:
        print(f"Error posting message: {e}")

def handle_button_click(ack, body, client, context):
    ack()

    action_id = body["actions"][0]["action_id"]
    if action_id == "button_1":
        specific_message = """Use esta thread para interagir com a <@U057233T98A> e criar seu briefing :smiling_face_with_3_hearts::blossom:"""

        user_id = body["user"]["id"]
        channel_id = body["channel"]["id"]

        try:
            response = client.chat_postMessage(
                channel=channel_id,
                text=specific_message
            )
            if response["ok"]:
                new_thread_ts_briefing = response['ts']
                test_set_thread_ts(new_thread_ts_briefing)
                time.sleep(1)  
            else:
                print("Failed to post new thread message.")
        except SlackApiError as e:
            print(f"Error posting message: {e}")
