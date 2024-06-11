#import time
#from slack_sdk import WebClient
#from slack_sdk.errors import SlackApiError

# Função para construir o menu de botões
def build_button_menu():
    buttons = [
        {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Briefing"
            },
            "value": "value_1",
            "action_id": "botao_brief"
        },
        {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Pauta"
            },
            "value": "value_2",
            "action_id": "botao_pauta"
        },
        # Adicione mais botões conforme necessário
    ]

    # Adiciona estilo aos botões
    for button in buttons:
        button['style'] = 'primary'

    # Bloco para os botões
    button_section = {
        "type": "actions",
        "elements": buttons
    }

    # Introdução
    intro_section = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": """*Olá, como posso te ajudar hoje? ✿*"""
        }
    }

    # Juntando todos os blocos
    sections = [intro_section, button_section]
    return sections

# Função para publicar o menu de botões
def menu_comandos(client, channel_id):
    try:
        result = client.chat_postMessage(
            channel=channel_id,
            text="Olá, como posso te ajudar hoje? ✿",
            blocks=build_button_menu()
        )
        print(result)
    except SlackApiError as e:
        print(f"Error posting message: {e}")

# Função para lidar com o clique do botão
def handle_button_click(ack, body, client, context):
    ack()
    user_id = body["user"]["id"]
    channel_id = body["channel"]["id"]
    action_id = body["actions"][0]["action_id"]
    thread_ts = body["message"]["ts"]  # Pega o timestamp da mensagem original para responder no mesmo thread

    if action_id == "botao_brief":
        # Envia uma mensagem para o usuário que clicou no botão
        send_message(client, channel_id, "Você é um assistente de briefing", thread_ts)
    else:
        # Aqui você pode adicionar sua lógica para lidar com cliques em outros botões
        print(f"Ação do botão {action_id} clicada")

# Função para enviar uma mensagem para o Slack
def send_message(client, channel_id, text, thread_ts=None):
    try:
        result = client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts  # Responde no mesmo thread se thread_ts for fornecido
        )
        print(result)
    except SlackApiError as e:
        print(f"Error posting message: {e}")