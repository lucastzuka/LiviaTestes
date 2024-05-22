from slack_sdk.errors import SlackApiError
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Variável global para armazenar o ID da thread do menu
thread_id_menu = None

def build_button_menu():
    # Definindo os botões com um loop para adicionar o estilo 'primary'
    button_texts = ["Gerente", "Midjourney", "Refs", "Briefing", "Pauta", "Tradutor"]
    button_values = ["!gerente", "!mid", "!refs", "!brief", "!pauta", "!tr"]
    buttons = []

    for i, text in enumerate(button_texts):
        button = {
            "type": "button",
            "text": {"type": "plain_text", "text": text},
            "value": button_values[i],
            "action_id": f"button_{i+1}",
            "style": "primary"
        }
        buttons.append(button)

    # Descrição dos botões
    descriptions = """
    𝗚𝗲𝗿𝗲𝗻𝘁𝗲: Gerencie seu projeto
    𝗠𝗶𝗱: Gerador de prompts para Midjourney
    𝗥𝗲𝗳𝘀: Pesquisa de referencias
    𝗕𝗿𝗶𝗲𝗳: Criador de briefing
    𝗣𝗮𝘂𝘁𝗮: Organizador de Pauta
    𝗧𝗿𝗮𝗱𝘂𝘁𝗼𝗿: Tradutor de textos
    """

    # Seções do bloco
    sections = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Olá, como posso te ajudar hoje? ✿*"}
        },
        {"type": "actions", "elements": buttons},
        {"type": "divider"},
        {
            "type": "context",
            "elements": [{"type": "plain_text", "text": descriptions, "emoji": True}]
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
    global thread_id_menu
    ack()

    # Mapeamento de action_id para comandos e mensagens específicas
    action_map = {
        "button_1": ("!gerente", "Você é uma assistente que ajuda a gerenciar projetos."),
        "button_2": ("!mid", "Você é uma assistente que ajuda a gerar prompts para Midjourney."),
        "button_3": ("!refs", "Você é uma assistente que ajuda a pesquisar referências."),
        "button_4": ("!brief", "A partir de agora seu nome é NBriefinzinho."),
        "button_5": ("!pauta", "Você é uma assistente que ajuda a organizar pautas."),
        "button_6": ("!tr", "Você é uma assistente que ajuda a traduzir textos.")
    }

    action_id = body["actions"][0]["action_id"]
    command, specific_message = action_map.get(action_id, (None, None))

    if not command:
        return

    user_id = body["user"]["id"]
    channel_id = body["channel"]["id"]

    # Enviar a mensagem específica dentro da thread do menu
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=specific_message,
            thread_ts=thread_id_menu  # Usar a thread do menu armazenada
        )
        print(response)
        
        # Imprimir o ID da thread no terminal
        if response["ok"]:
            print(f"Thread ID: {response['thread_ts']}")
        else:
            print("Failed to post message to thread.")
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
        app.command("/menu")(lambda ack, body, client: ack() or menu_comandos(client, body['channel_id']))
        
        # Configuração para lidar com cliques de botões
        app.action("button_1")(lambda ack, body, client, context: handle_button_click(ack, body, client, context))
        app.action("button_2")(lambda ack, body, client, context: handle_button_click(ack, body, client, context))
        app.action("button_3")(lambda ack, body, client, context: handle_button_click(ack, body, client, context))
        app.action("button_4")(lambda ack, body, client, context: handle_button_click(ack, body, client, context))
        app.action("button_5")(lambda ack, body, client, context: handle_button_click(ack, body, client, context))
        app.action("button_6")(lambda ack, body, client, context: handle_button_click(ack, body, client, context))

        # Inicializar a aplicação
        handler = SocketModeHandler(app, app_token)
        handler.start()
