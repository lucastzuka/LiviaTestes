import os
import json
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=SLACK_BOT_TOKEN)


blocks= [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "`𖡻 🆁🅴🅵🆁🅴🆂🅷 🅻🅸🆅🅸🅰 ♡ #15 `"
        }
    },
    {
        "type": "context",
        "elements": [
            {
                "text": "4 de Junho, 2024  |  Notícias sobre IA e inovação",
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
            "text": "*Bom dia, Livers!* 💛\n\nRapidinho: Adobe enfrenta críticas por vender imagens de IA, descontos no uso do ChatGPT para universidades e ONGs, startup lança computadores 'vivos', OpenAI firma parcerias com Vox Media e The Atlantic, Apple reformula Siri com IA."
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "<https://www.theverge.com/2024/6/3/24170285/adobe-stock-ansel-adams-style-ai-generated-images|*`🏞️ Adobe Repreendida por Vender Imagens de IA`*>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Adobe enfrenta críticas por vender imagens de IA no estilo Ansel Adams no Adobe Stock.```1️⃣ Acervo de Adams denuncia uso não autorizado do nome 📸\n2️⃣ Adobe removeu conteúdo e entrou em contato com o acervo de Adams 📞\n3️⃣ Políticas da Adobe proíbem uso de nomes de artistas sem autorização 📜\n4️⃣ Acervo de Adams pede ação proativa da Adobe para proteger propriedade intelectual 🎨\n5️⃣ Controvérsia ressalta a tensão entre criadores de conteúdo e plataformas de IA 🤔```\nEssa controvérsia destaca a importância de proteger a propriedade intelectual na era digital. A crescente tensão entre criadores de conteúdo e plataformas de IA mostra a necessidade de regras claras para o uso de obras de arte geradas por IA."
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "<https://www.theverge.com/2024/5/31/24168574/openai-chatgpt-schools-nonprofits-discounts|*`✨ OpenAI Torna o ChatGPT Mais Acessível para Escolas e ONGs`*>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "OpenAI oferece descontos no uso do ChatGPT para universidades e ONGs.```1️⃣ ChatGPT Edu permite uso responsável de IA em universidades 🎓\n2️⃣ Descontos para ONGs: ChatGPT Team por $20/mês e Enterprise com 50% de desconto 💼\n3️⃣ Ferramentas para revisar currículos, pedidos de financiamento e mais 📚\n4️⃣ Dados não são usados para treinar modelos da OpenAI 🔒\n5️⃣ Esforço contínuo para democratizar o acesso à IA em setores educacionais 🎯```\nEssas iniciativas mostram o compromisso da OpenAI em democratizar a IA. Mesmo enfrentando críticas e demissões internas, a OpenAI continua a ampliar o acesso à sua tecnologia, especialmente em setores que podem se beneficiar significativamente dessa inovação."
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "<https://www.tomshardware.com/pc-components/cpus/worlds-first-bioprocessor-uses-16-human-brain-organoids-for-a-million-times-less-power-consumption-than-a-digital-chip|*`🧬 Startup Suíça Treina Computadores “Vivos”`*>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "FinalSpark lança a Neuroplatform, usando células cerebrais vivas para computação.```1️⃣ Utiliza organoides cerebrais humanos como bioprocessadores 🧠\n2️⃣ Combina peças tradicionais de computador com células vivas 🖥️\n3️⃣ Bioprocessadores consomem 1 milhão de vezes menos energia ⚡\n4️⃣ Futuro promissor, mas ainda longe de escalar para grandes modelos de IA 🚀\n5️⃣ Explorando novas fronteiras da biocomputação e sustentabilidade 🌿```\nBiocomputadores podem revolucionar o consumo de energia em centros de dados de IA. Embora a tecnologia ainda esteja em estágio inicial, a promessa de uma computação mais eficiente e sustentável é intrigante e pode mudar o futuro da tecnologia."
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "<https://www.theverge.com/2024/5/29/24167072/openai-content-copyright-vox-media-the-atlantic|*`🗞️ OpenAI Adiciona Grandes Parceiros de Notícias`*>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "OpenAI firma parcerias com Vox Media e The Atlantic para conteúdo e produtos.```1️⃣ ChatGPT acessa conteúdo de Vox, The Verge, NY Magazine, entre outros 📰\n2️⃣ Conteúdo do The Atlantic disponível nos produtos da OpenAI 🌐\n3️⃣ Programa global de aceleração para 128 redações com WAN-IFRA 🏢\n4️⃣ Controvérsia sobre parcerias de mídia com empresas de IA 🧐\n5️⃣ Ferramentas de IA podem melhorar eficiência, mas trazem desafios ⚙️```\nAs parcerias mostram a adaptação das empresas de mídia às ferramentas de IA, apesar dos desafios. A colaboração com grandes nomes da mídia pode oferecer uma nova dimensão à criação e distribuição de conteúdo, mas também levanta questões sobre dependência e controle de dados."
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "<https://www.theverge.com/2024/5/30/24168175/ios-18-ai-siri-apple-apps|*`🗣️ Siri 2.0 Permitirá Controle de Aplicativos com IA`*>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Apple reformula Siri com IA para controle avançado de aplicativos por voz.```1️⃣ Modelos de linguagem permitem comandos mais complexos 🗣️\n2️⃣ Análise de hábitos do usuário para novos comandos automáticos 📈\n3️⃣ Resumo de artigos, edição de fotos, envio de e-mails e mais 📱\n4️⃣ Tarefas múltiplas planejadas para o próximo ano 🗓️\n5️⃣ Atualização visa melhorar a utilidade e integração da Siri com apps 🚀```\nA atualização da Siri promete uma experiência mais útil e integrada para os usuários. Com comandos mais complexos e análise de hábitos, a Siri 2.0 pode transformar a forma como interagimos com nossos dispositivos, tornando a assistente virtual mais eficiente e intuitiva."
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*`RAPIDINHAS`*"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "A <https://finance.yahoo.com/news/microsoft-invest-3-2-bn-131501138.html|Microsoft> anunciou um investimento de US$ 3,2 bilhões na infraestrutura de IA e nuvem da Suécia, visando treinar 250 mil trabalhadores até 2027."
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Fundador da Zoom, Eric Yuan disse em uma entrevista ao The Verge que os avatares de IA <https://www.theverge.com/2024/6/3/24168733/zoom-ceo-ai-clones-digital-twins-videoconferencing-decoder-interview|gêmeos digitais> eventualmente participarão de reuniões e tomarão decisões em nome do usuário."
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": " <https://x.com/DillToma/status/1795180305210315206|Mr.Beast> lançou novas ferramentas para sua plataforma ViewStats Pro, incluindo uma pesquisa de thumbnails com tecnologia que permite encontrar inspiração com prompts em linguagem natural."
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Nvidia apresentou o <https://nvidianews.nvidia.com/news/nvidia-brings-ai-assistants-to-life-with-geforce-rtx-ai-pcs|Project G-Assist>, um assistente de jogos que oferece ajuda contextual e respostas personalizadas para jogos de PC."
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "A OpenAI está relançando sua <https://x.com/kenrickcai/status/1796263952818811034|equipe de robótica> para desenvolver modelos para robôs de outras empresas em vez de criar seu próprio hardware."
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Nvidia apresenta o Earth-2, gêmeo digital do planeta Terra para diversos usos, incluindo simulação de previsão climática precisa que considera todas as construções do planeta. Veja o video abaixo!"
        }
    },
    {
        "type": "divider"
    },
    {
        "dispatch_action": True,
        "type": "input",
        "element": {
            "type": "plain_text_input",
            "placeholder": {
                "type": "plain_text",
                "text": " "
            },
            "dispatch_action_config": {
                "trigger_actions_on": [
                    "on_enter_pressed"
                ]
            },
            "action_id": "plain_text_input-action"
        },
        "label": {
            "type": "plain_text",
            "text": ":bellhop_bell: Dúvidas ou sugestões?",
            "emoji": True
        }
    },
    {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "Para resposta, identifique-se, pois esta caixinha é *anônima!* <3"
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
            "text": "Até *quinta-feira*, galera! :kissing_heart:"
        }
    }
]
video_paths = [
    r"C:\Users\LiveBot\Downloads\Krea Real-time.mp4",
    r"C:\Users\LiveBot\Downloads\Nvidia Earth-2.mp4",
    #r"C:\Users\LiveBot\Downloads\eyes.mp4"
]

try:
    response = client.chat_postMessage(
        channel='testes',
        blocks=json.dumps(blocks),
        unfurl_links=False
    )
    assert response["ok"]
    
    # Fazer upload dos vídeos
    for video_path in video_paths:
        if os.path.exists(video_path):
            video_upload_response = client.files_upload(
                channels='testes',
                file=video_path,
                title=f"{os.path.basename(video_path)}"
            )
            assert video_upload_response["ok"]
        else:
            print(f"O arquivo de vídeo não foi encontrado no caminho especificado: {video_path}")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
       