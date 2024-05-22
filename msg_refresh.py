import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = "xoxb-2219409494181-5240105927282-i4GnrjCXM65neAI7pwAowYK5"
client = WebClient(token=slack_token)
video_path = r"C:\Users\LiveBot\Downloads\Boston Atlas.mp4"

blocks= [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "`𖡻 🆁🅴🅵🆁🅴🆂🅷 🅻🅸🆅🅸🅰 ♡ #4 `"
        }
    },
    {
        "type": "context",
        "elements": [
            {
                "text": "18 de Abril, 2024 | Notícias sobre IA e inovação",
                "type": "mrkdwn"
            }
        ]
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Bom dia, Livers!* 💛\n\nRapidinho: Boston Dynamics apresenta novo robô Atlas, Logitech renova mouses com botão de IA e avanços da IA no tratamento de Parkinson."
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "<https://www.theverge.com/2024/4/17/24132468/logitech-ai-prompt-builder-button|*`🖱️ Logitech Introduz Botão de IA em Novos Mouses`*>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "A Logitech inova trazendo o botão dedicado à IA em seus mouses, uma pequena revolução no acesso à tecnologia de assistentes virtuais.```1️⃣ O Signature AI Edition M750 traz o Logi AI Prompt Builder, não apenas um chatbot, mas um criador de prompts personalizados 🤖\n2️⃣ Compatível apenas com modelos recentes, o novo M750 facilita a criação e reestruturação de textos com um simples clique 🖱️\n3️⃣ Atualmente, funciona apenas em inglês e exclusivamente com o ChatGPT, mas há planos de expansão e compatibilidade futura 🌐```\nEnquanto o futuro dos PCs pode incluir teclas de IA integradas, a Logitech se antecipa e oferece uma nova forma de interação diária com a inteligência artificial."
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "<https://www.cam.ac.uk/research/news/ai-speeds-up-drug-design-for-parkinsons-ten-fold|*`💊 IA Acelera Tratamento para Parkinson`*>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Pesquisadores da Universidade de Cambridge desenvolveram uma metodologia de IA para acelerar a descoberta de tratamentos para a doença de Parkinson.```1️⃣ A IA analisa milhões de compostos para identificar aqueles que impedem a formação de aglomerados proteicos nocivos 🧬\n2️⃣ Os compostos mais promissores são testados em laboratório, refinando o processo iterativamente 🔬\n3️⃣ Este método resultou na descoberta de cinco compostos altamente eficazes, muito superiores aos anteriores 💪```\nA capacidade da IA de reduzir tempo e custos na pesquisa médica promete uma nova era de descobertas, trazendo esperança para o tratamento de doenças complexas."
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Até *terça-feira*, galera! :kissing_heart:"
        }
    }
]


try:

    response = client.chat_postMessage(
        channel='testes',
        blocks=json.dumps(blocks),
        unfurl_links=False  # Isso deve ser passado como argumento aqui
    )
    
    assert response["ok"]
    
        # Verificar se o arquivo de vídeo existe antes de tentar fazer o upload
    if os.path.exists(video_path):
        # Fazer upload do vídeo
        video_upload_response = client.files_upload(
            a,
            file=video_path,
            title="Boston Atlas"
        )
        assert video_upload_response["ok"]
    else:
        print("O arquivo de vídeo não foi encontrado no caminho especificado.")
        
except SlackApiError as e:
    # Caso ocorra algum erro.
    print(f"Erro ao enviar mensagem: {e.response['error']}")
