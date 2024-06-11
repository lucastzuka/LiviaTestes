from slack_sdk.errors import SlackApiError
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Variável global para armazenar o ID da thread do menu
thread_id_menu = None
# Variável global para armazenar o ID da nova thread do briefing
new_thread_ts_briefing = None

def build_button_menu():
    # Definindo o botão "Briefing" com estilo 'primary'
    button_text = "Briefing"
    button_value = "!brief"
    button = {
        "type": "button",
        "text": {"type": "plain_text", "text": button_text},
        "value": button_value,
        "action_id": "button_1",
        "style": "primary"
    }

    # Descrição do botão
    description = """
    𝗕𝗿𝗶𝗲𝗳: Criador de briefing
    """

    # Seções do bloco
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
        print(result)
        
        # Armazenar o ID da thread do menu
        if result["ok"]:
            thread_id_menu = result['ts']
            print(f"Thread ID of the menu: {thread_id_menu}")
        else:
            print("Failed to post menu message to thread.")
    except SlackApiError as e:
        print(f"Error posting message: {e}")

def handle_button_click(ack, body, client, context):
    global new_thread_ts_briefing
    ack()

    # Mapeamento de action_id para comando e mensagem específica
    action_map = {
        "button_1": ("!brief", "A partir de agora seu nome é NBriefinzinho.")
    }

    action_id = body["actions"][0]["action_id"]
    command, specific_message = action_map.get(action_id, (None, None))

    if not command:
        return

    user_id = body["user"]["id"]
    channel_id = body["channel"]["id"]

    # Enviar a mensagem específica criando uma nova thread
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=specific_message
        )
        print(response)
        
        # Armazenar o ID da nova thread no terminal
        if response["ok"]:
            new_thread_ts_briefing = response['ts']
            print(f"New Thread ID: {new_thread_ts_briefing}")
        else:
            print("Failed to post new thread message.")
    except SlackApiError as e:
        print(f"Error posting message: {e}")

# Inicializar a aplicação
if __name__ == "__main__":
    app_token = os.getenv("SLACK_APP_TOKEN")
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    
    if not app_token or not bot_token:
        print("Missing SLACK_APP_TOKEN or SLACK_BOT_TOKEN environment variables.")
    else:
        app = App(token=bot_token)

        # Configuração de eventos e comandos
        app.command("/teste_menu")(lambda ack, body, client: ack() or menu_comandos(client, body['channel_id']))
        
        # Configuração para lidar com cliques de botão
        app.action("button_1")(lambda ack, body, client, context: handle_button_click(ack, body, client, context))

        # Inicializar a aplicação
        handler = SocketModeHandler(app, app_token)
        handler.start()
