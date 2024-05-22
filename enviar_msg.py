import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Função para enviar um bloco de mensagens
def send_message(client, channel, blocks):
    try:
        response = client.chat_postMessage(channel=channel, blocks=json.dumps(blocks))
        assert response["ok"]
        print("Mensagem enviada com sucesso.")
    except SlackApiError as e:
        print(f"Erro ao enviar mensagem: {e.response['error']}")

# Função para enviar arquivo
def send_file(client, channel, file_path, title):
    try:
        response = client.files_upload(channels=channel, file=file_path, title=title)
        assert response["ok"]
        print("Arquivo enviado com sucesso.")
    except SlackApiError as e:
        print(f"Erro ao enviar arquivo: {e.response['error']}")

# Token e cliente do Slack
slack_token = "xoxb-2219409494181-5240105927282-i4GnrjCXM65neAI7pwAowYK5"
client = WebClient(token=slack_token)

# Canal alvo
channel = 'general'  # Defina aqui o nome do canal

blocks = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": """*E aí, Livers!* :rainbow:

Preparem-se para ter suas mentes explodidas!
A edição #3 da nossa newsletter `𖡻 🆁🅴🅵🆁🅴🆂🅷 🅻🅸🆅🅸🅰 ♡` chegou com novidades que vão fazer os nossos criativos pirarem! :exploding_head:
A *Adobe* está revolucionando o Premiere com IA, e agora você poderá *GERAR* vídeos diretamente na timeline! É a fusão perfeita entre IA e edição de vídeo, e no canal de inovação postamos uma demo surpreendente dessa novidade.
É inovação que não acaba mais!
Além disso, temos IA redefinindo interações com as novas estratégias de engajamento da *Meta* e *TikTok*.
E não para por aí: os robôs do Google DeepMind estão mostrando que até no futebol eles têm habilidade. *_Alô Max, vem ai uma nova liga?_* :yellow_heart::soccer:

Não fiquem de fora dessa! Corram para o canal *#inovação* e confiram a newsletter que está deixando todo mundo de queixo caído.
Até mais, e vamos que vamos, porque a inovação não espera! :rocket::robot_face:"""
        }
    }
]

# Envio da mensagem com o link do áudio
send_message(client, channel, blocks)

