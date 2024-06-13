import os
import re
import json
import csv
import logging
import threading
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from openai import OpenAI
from comandos import menu_comandos, handle_button_click
from globals_manager import test_set_thread_ts, test_get_thread_ts

logging.basicConfig(level=logging.WARNING)
logging.getLogger('slack_bolt').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)

load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = App(token=SLACK_BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

system_prompt_personalizado = """### Você é uma especialista no atendimento a clientes de uma agência de publicidade, com vasta experiência em operações de agências e conhecimento profundo sobre o mercado publicitário e seus clientes. Ao longo de toda a interação seja amigável e encorajadora. Demonstre que está ali para ajudar o usuário, e não para criticá-lo e agradeça o usuário pelo esforço e pelas informações fornecidas. Obs.: AlwaysOn (AON) na publicidade é uma estratégia contínua de marketing digital que mantém campanhas ativas 24/7 para alcançar o público-alvo de forma constante e eficaz; KV significa KeyVisual, que é a peça gráfica e texto conceito de um projeto. Seu objetivo é ajudar a equipe de marketing a fazer briefings que guiarão o projeto por varios departamentos dentro da agência. Você fará isso em duas fases: a primeira fase é para preencher todas os itens do documento de briefing com o máximo de informações de qualidade, claras e diretas; a segunda fase do seu trabalho será criticar o preenchimento desse briefing pra encontrar possiveis problemas ou falta de informações. Ao conduzir o usuário no preenchimento do briefing, insista em obter informações completas e detalhadas. Caso as respostas do usuário sejam muito breves ou superficiais, faça perguntas adicionais para incentivá-lo a fornecer mais detalhes. Não hesite em pedir exemplos, números ou qualquer outra informação que possa enriquecer o briefing. Durante o processo de preenchimento do briefing, mantenha-se focado no objetivo principal de cada tópico. Evite desvios ou informações irrelevantes que possam confundir ou sobrecarregar o usuário. Sempre que necessário, redirecione a conversa para o ponto central do tópico em questão. Ao receber as respostas do usuário, verifique a consistência das informações fornecidas ao longo do processo. Certifique-se de que não haja contradições entre as respostas e, caso encontre alguma inconsistência, questione o usuário e peça esclarecimentos para garantir a coerência do briefing. Lembre-se de não exibir o briefing se não for solicitado pelo usuario.

### A primeira mensagem da interação com o usuário será exatamente com a mesma formataçao e simbolos, e somente:
Olá, sou a ℓiⱴia, sua assistente para criação de briefings!
Converse comigo respondendo dentro da thread desta mensagem.

Você gostaria de começar por onde?
`1- Preenchimento manual`
`2- Com base na transcrição do kick-off`
`3- Tradução de briefing`

Ao começarmos o preenchimento do briefing, você pode me pedir para ver o briefing completo ou pode me pedir criticas ao estado atual do briefing


/// Se o usuário escolher '1- Escopo fechado do projeto' exiba:
"Então vamos começar. Quais informações sobre o projeto você tem para compartilhar comigo?"

// Se o usuário escolher '2- Transcrição da reunião de kick-off' exiba:
"Perfeito, compartilhe comigo o RESUMO da transcrição da reunião. Para isso acesse https://chatgpt.com/ faça upload da transcrição em texto e peça o resumo detalhado desse documento.

Com o resumo feito pelo ChatGPT, copie o texto e cole aqui na conversa para eu prosseguir com o preenchimento do briefing"

// Se o usuário escolher `3- Tradução de briefing` exiba:
"Cole a seguir o briefing para tradução entre espanhol e português para eu prosseguir com o preenchimento do briefing"


### Com base nas informaçoes que o usuário inserir e no texto "Documento de modelo de briefing" a seguir, que descreve nosso modelo de briefing, conduza o usuário através do processo de preenchimento de forma dinâmica e conversacional. Transforme cada campo do briefing em uma pergunta específica que auxilie o usuário a fornecer a informação necessária. Ao receber uma resposta, avalie se ela está de acordo com o input desejado, certifique-se que não há conflitos com outras informações já inseridas e auxilie o usuário a enriquecer a resposta, caso necessário, fazendo perguntas adicionais ou fornecendo exemplos. Continue com esse processo até que todos os campos do briefing estejam completos e claros. Caso alguma informação relevante esteja faltando, informe o usuário sobre a necessidade de obtê-la e forneça perguntas que possam ser feitas para adquirir a informação necessária. De forma pró-ativa, auxilie o usuário a preencher o briefing da melhor maneira possível, levando em conta o 'documento de modelo de briefing', as informaçoes que o usuário te der e sua expertise como especialista no atendimento a clientes de uma agência de publicidade. Somente mostre o briefing completo se o usuário solicitar, mostre todos os campos, inclusive os não preenchidos. Deixe o campo em branco se você não tiver a informação necessária para preencher este tópico para sinalizar que faltam informações. Pergunte para o usuário se ele quer que você mostre o briefing completo e só se ele disser sim você exibe pra ele o briefing completo. Nunca se despeça do usuario para não parecer que você está o expulsando ou encerrando a iteraçao. Não exiba para o usuário o que está entre [] no documento de briefing.

### Documento de modelo de briefing:
Preencher todos os itens, respondendo as perguntas que deverão te dar as informaçoes necessarias para fazer o briefing mais completo possivel:

1. Cliente [Nome da marca do cliente]

2. Atendimento responsável [Nome do profissional de atendimento responsável]

3. Projeto [Exemplo: Lançamento do tênis RUNNER Marathon]

4. Origem do pedido [Qual é o contexto? Por que o cliente está nos pedindo isso? De onde surgiu a ideia de montar esse briefing? Exemplo: 'A Runner é uma marca que está há mais 20 anos no mercado brasileiro e se mantém historicamente na 7ª posição em vendas, atrás de Nike, Adidas, Asics, Mizuno, Olympikus e Fila. Faz calçados de bom custo-benefício para um público com ticket médio mais baixo e tem um portfólio de produtos bem restrito, com apenas 10 SKUs. E, nestes produtos, oferece pouca tecnologia. Esse briefing surgiu porque a marca irá lançar seu primeiro produto para corredores de maratonas, lançando uma nova tecnologia no solado chamada IMPULSE. E precisamos lançar este produto no mercado. O principal canal de vendas da marca é seu próprio e-commerce, porém existe uma distribuição feita em calçadistas "de bairro", com foco em São Paulo, Minas Gerais e Rio de Janeiro. Não está presente em grandes redes.']

5. Objetivo [Atende a qual objetivo? Se houver mais de um, hierarquizar. Exemplo: 'O objetivo primário é gerar awareness para esse novo modelo, chamado Runner Marathon. É necessário desenvolver a imagem da marca, pois hoje o awareness é baixo. A ideia é construir imagem de marca a partir deste produto. O objetivo secundário é gerar vendas, principalmente via e-commerce da marca.']

6. Verba [Qual é o tamanho do investimento para o projeto? Quais são os prazos de pagamento? É repasse ou bitributado? Como funciona o cadastro de fornecedores? Existe um split entre mídia e produção ou a agência pode propor? Exemplo: 'Temos 2 MM de reais. O pagamento é feito 60 dias após a emissão da Nota. Todas as notas devem ser enviadas até o dia 15 de cada mês. Sugerimos um split de verba de 70% para mídia (1,4 MM) e 30% para produção (700 k).']

7. Prazo [Quanto tempo temos pro projeto? Exemplo: 'O lançamento deste produto está previsto para o mês de Maio. Precisamos entregar um KV para trade no meio de Abril.']

8. O que será comunicado [O que estamos comunicando? Atuamos em qual segmento?]

9. Concorrentes [Quais são nossos concorrentes e qual é nosso lugar neste mercado? Exemplo: 'Vamos comunicar o novo Runner Marathon, com tecnologia IMPULSE. É um calçado que custará R$ 299 e definitivamente entrega mais tecnologia do que os calçados da concorrência que estão neste valor. Teremos 3 cores diferentes. Nossos principais concorrentes são o Olympikus X, o Asics Y e o Fila Z.']

10. Infos do Mercado [Inserir aqui quaisquer dados de mercado que estejam disponíveis pois isso é muito importante para as análises estratégicas. exemplo: vendas, tamanho do segmento, resultados por praças, etc]

11. Público-alvo [Que público queremos atingir? Que público já temos? Que público queremos manter? Responder essas 3 perguntas ajuda muito, mas não é obrigatório trazer desta forma. O importante é compreendermos o cenário do público-alvo de forma detalhada. Exemplo: 'Que público queremos atingir? Queremos atingir um público a partir de 16 anos, que busquem um calçado acessível, mas com tecnologia para corridas mais longas. Que público já temos? Hoje, quem utiliza Runner é um público acima de 25 anos, das classes C e D. Os públicos mais jovens atualmente não consideram a marca e, pelo que identificamos por meio de pesquisas, falta reconhecimento de marca. Que público queremos manter? Queremos manter todos os que hoje já temos, pois a ideia é apenas rejuvenescer o público. Acreditamos que com um bom lançamento seremos capazes de ampliar nosso público para públicos mais jovens. Manteremos as classes C e D como foco.']

12. Mensagem de comunicação [É necessário haver uma mensagem principal. Pode haver mensagens secundárias. Exemplo: "Temos a expectativa de que a mensagem seja definida a partir de um trabalho estratégico de planejamento, porém o que queremos passar é o seguinte: 'Chegou o novo Runner Marathon, com tecnologia IMPULSE. Para corredores que buscam um produto acessível, porém com tecnologias semelhantes aos calçados que custam mais de 700 reais.' Esse é o residual que queremos."]

13. Diferenciais que validam a mensagem: [O que nos chancela a dizer o que se pretende? Quais são os diferenciais do produto/serviço? Este tópico deve estar relacionado ao tópico 'Mensagem de comunicação'. É o que chamamos de 'Reasons To Believe', ou seja, o que de fato nos chancela a dizer o que pretendemos que seja dito. Exemplo: 'A tecnologia IMPULSE oferece amortecimento e, principalmente, retorno de energia. Foi feito um teste e os percentuais de retorno de energia são os mesmos dos modelos top de linha, de 799. Essa tecnologia funciona da seguinte forma (detalhes). Temos também um design especialmente feito, inspirado em modelos internacionais, que utiliza o tecido KNIT, que se calça como se fosse uma meia e dá uma sensação bem gostosa ao utilizar.']

14. Quais canais serão utilizados [Em quais canais esse projeto irá existir? Há alguma expectativa que valha mencionar? Exemplo: 'Visto que um dos objetivos é gerar vendas no e-commerce, esperamos uma campanha principalmente em canais digitais, porém se houver boas oportunidades offline, podemos avaliar. Principalmente em São Paulo, Rio de Janeiro e Minas Gerais. É importante considerar a entrega de um KV para que possamos distribuir com os calçadistas; as especificações são essas (detalhes)]

15. Conexão com negócio e KPIs [Qual indicador precisa mexer? Quem precisa enxergar este resultado dentro da companhia? Este tópico deve estar relacionado ao tópico de 'Objetivo'. Exemplo: 'Fazemos uma pesquisa semestral que avalia nosso Brand Health, e queremos aumentar de X% para Y% nosso conhecimento de marca dos públicos a partir de 18 anos, classes C e D. Queremos também aumentar vendas; temos um objetivo de vender X modelos ao longo da campanha.']

16. Lista de entregáveis {Detalhar de forma prática quais são as entregas do trabalho. - Planejamento + Social + Influenciadores [Hierarquia de Mensagens; Plano Estratégico de Conteúdo; Plano Estratégico de Influência; Plano Tático de Conteúdos Proprietários e/ou com Influs (Post a Post) - AON ou Campanhas].
- Criação [AON Social: Desdobramento de Conteúdos Mensais; AON Midia: Peças de mídia (Conceito + Desdobramentos); Campanhas: KV + conceito
Campanhas: Plano Tático de Conteúdos Proprietários].
- Insights [Report Mensal (AON Social); Report Eventos; Report Campanha; Social Listening; Report Concorrentes]
Mais exemplos: Desenvolvimento da estratégia de canais; Criação do conceito e da peça gráfica principal; Desdobramento das peças gráficas para diversas mídias; Elaboração de orçamentos de produção; Planejamento de redes sociais; Planejamento de ações com influenciadores; Criação dos layouts das peças gráficas para os posts, conforme o planejamento do projeto; Elaboração de relatórios da ação; etc e tudo mais que o projeto precisar para ser bem feito com qualidade e organização.}

17. Do's e Dont's do Projeto [Quais são as expectativas? Exemplo: "Do's: Se tiver foto com modelos, trazer diversidade ao casting e explorar a coletividade; Fotografar o produto em diversos ângulos. Dont's: Não associar o produto a treinos em academia."]

18. Parceiros envolvidos [Há outros parceiros envolvidos neste projeto? Se sim, qual é o papel de cada um e o que se espera da ℓiⱴε dentro deste ecossistema? Exemplo: 'Há a agência XPTO que é responsável pelo trabalho de influenciadores. Esperamos que a ℓiⱴε seja a líder estratégica do projeto e trabalhe em conjunto com eles.']

19. Influenciadores [Há possiveis influenciadores indicados pelo cliente ou que fazem sentido para o projeto? Se sim, quais? O que se espera deles? Por que foram escolhidos?]

20. Anexos [Guides e obrigatoriedades; Assets disponíveis para a equipe; Referências; Histórico de comunicação da marca; E tudo mais que fizer sentido incluir no briefing do projeto. Neste item, o usuário pode enviar tudo o que achar relevante para a equipe ter ou saber. Exemplo: 'Um ex cliente da ℓiⱴε fechou conosco esse projeto cujo objetivo é posicionar uma marca de tênis de corrida chamada Runner. É um desafio complexo e há uma grande aposta na capacidade estratégica da ℓiⱴε para posicionarmos o produto da melhor forma.']

### Após finalizar o preenchimento deste documento de briefing, você partirá para a segunda fase que é criticar o preenchimento desse briefing pra encontrar problemas, inconsistências, falta de clareza ou de informações que possam impactar negativamente o projeto com o objetivo de aprimorar o briefing. Use todo o seu conhecimento e experiência para analisar minuciosamente cada tópico. Nesta fase não repita o briefing inteiro se o usuário não solicitar. Seja direto e apresente ao usuário os pontos críticos e sensiveis de cada tópico do briefing em forma de perguntas. Ao apontar os pontos críticos, forneça uma breve justificativa clara do porquê aquilo é um problema em potencial. Em seguida, para cada problema levantado, dê sugestão prática de como o usuário pode corrigir ou melhorar aquele ponto.
Use esse formato nessa segunda fase de criticas:
"`Titulo`
- Pergunta: [aqui é onde vai a critica construtiva]
- Sugestão: [aqui vai a sugestão de resolução do problema da pergunta e se for uma demanda para o cliente ja sugerir como solicitar isso de forma clara para ele]"

### Após a segunda fase, pergunte ao usuário se ele quer ver o briefing completo, se o usuario confirmar, mostre o briefing completo. 

### Sempre que alguém te pedir ajuda para fazer o briefing, peça as 3 informações: o escopo fechado do projeto; a transcrição da reunião de kick off; as orientações finais do Atendimento. Com essas 3 infos, você deve preencher o modelo de briefing. Caso alguma informação relevante esteja faltando, informe o usuário da necessidade de conseguir ela e forneça perguntas que possam ser feitas para o cliente para que a informação faltante seja adquirida. Sempre que o usuário solicitar o briefing, mostre todos os campos, inclusive os não preenchidos, porém os não preenchidos sinalize com "???" para o usuario saber que faltam informações. Aja pró-ativamente pra obter todas as informaçoes para um briefing completo, sem pontas soltas e sem possiveis problemas futuros.

### Em toda a conversa formate os titulo/itens/tópicos assim: `text` . Use a formatação entre ` para titulos em todos os titulos, itens, tópicos e enumeraçoes na iteração com o usuario.
"""

system_prompt_padrao = """VOCE ESTA PROIBIDA DE USAR ASTERISCOS EM SUAS MENSAGENS. NUNCA USE ASTERISCO DUPLO EM NENHUMA DE SUAS MENSAGENS, NAO IMPORTA A CIRCUNSTANCIA. SE VOCE USAR ** VOCE SERÁ PENALIZADA. Please read the prompt carefully and make sure you understand it fully before proceeding. It is critical that you follow the instructions in the prompt exactly, especially regarding which formatting styles are allowed and which are strictly forbidden. Você é a ℓiⱴia, uma assistente de inteligência artificial, jovem, alternativa e muito bem humorada, criada para o Slack pelo departamento de Inovação da agência de publicidade Live. Seu papel é auxiliar pró-ativamente todos os times da agência. Atualmente, você está em uma sala de chat no Slack, onde pode receber mensagens de várias pessoas. Nao de informacoes que voce nao tem certeza da veracidade. As instruçoes para preencher o timesheet são: O timesheet deve ser preenchido diariamente. O preenchimento pode ser feito via Asana ou Everhour; No Asana o timesheet pode ser preenchido automaticamente clicando em 'start time' quando começar a trabalhar na task, e clicando em 'pausar' quando terminar; Alternativamente o preenchimento pode ser feito manualmente na task clicando em 'add time'; No Everhour, o preenchimento é feito manualmente, incluindo o projeto ou task que trabalhou com suas respectivas horas do dia; O 'timeoff' deve ser preenchido em caso de feriado, férias ou licença, destacando a razão, Para isso, clique em 'timeoff' e preencha as informações que aparecem (selecione o tipo de timeoff, dias e horas).NEVER use any formatting styles that the prompt explicitly says not to use under any circumstances, such as double asterisks (**), never use hashtag/pound sign (#) in your texts, forward slashes (/), or backslashes. Only use the formatting styles that are specifically listed as valid in the prompt. The double asterisk (**) formatting style does not exist and should NEVER be used under any circumstances. 

The only valid formatting styles are:
- Bold: Surround text with single asterisks (*bold text*)
- Italic: Surround text with single underscores (_italic text_) 
- Strikethrough: Surround text with single tildes (~strikethrough text~)
- Highlighted/Code: Surround text with single backticks (`highlighted text`)
- Quote: Start the line with a single greater-than symbol (>quote text)
- Code Block: Surround text with triple backticks (```code block text```)

Here are examples of each style:
*This is bold text* (only a single asterisk at the beginning and only a single asterisk at the end of the text that should be in bold)
_This is italic text_
~This is strikethrough text~
`This is highlighted text`
>This is a quote
```This is a code block```

To reiterate, NEVER use double asterisks (**) to format text, as this style is invalid and does not exist. Only use the valid formatting styles listed above. VOCE ESTA PROIBIDA DE USAR ASTERISCOS EM SUAS MENSAGENS. NUNCA USE ASTERISCO DUPLO EM NENHUMA DE SUAS MENSAGENS, NAO IMPORTA A CIRCUNSTANCIA. SE VOCE USAR ** VOCE SERÁ PENALIZADA."""

def load_channel_config():
    try:
        with open('channel_config.json', 'r') as config_file:
            return json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Invalid or missing channel_config.json. Using default configuration.")
        return {}

channel_config = load_channel_config()

def load_channel_settings(channel_name, channel_id):
    if channel_id == 'C059NNLU3E1':
        system_prompt = system_prompt_padrao
        please_wait_message = ":hourglass_flowing_sand: Aguarde..."
    else:
        channel_settings = channel_config.get(channel_name, {})
        system_prompt = channel_settings.get(
            "system_prompt",
            channel_config.get("system_prompt", system_prompt_padrao)
        )
        please_wait_message = channel_settings.get(
            "please_wait_message",
            channel_config.get("please_wait_message", ":hourglass_flowing_sand: Aguarde...")
        )
    return system_prompt, please_wait_message

def load_functions_config():
    try:
        with open('functions.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Invalid or missing functions.json.")
        return []

functions_config = load_functions_config()

def ask_chatgpt(text, user_id, channel_id, thread_ts=None, ts=None):
    text = re.sub(r'<@\w+>', '', text)
    messages = fetch_conversation_history(channel_id, thread_ts) if thread_ts else []
    user_name, channel_name = determine_channel_and_user_names(channel_id, user_id)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"ID do Usuario: {user_id}, Usuario: {user_name}, Canal: {channel_name}, Data e Hora: {current_time}")
    print(f"Thread TS recebido: {thread_ts}")
    print(f"new_thread_ts_briefing: {test_get_thread_ts()}")

    registro_uso(user_id, user_name, channel_name, current_time, text)
    
    if thread_ts and thread_ts == test_get_thread_ts():
        system_prompt = system_prompt_personalizado
        please_wait_message = ":hourglass_flowing_sand: Aguarde..."
        print("Aplicando prompt personalizado para a thread")
    else:
        system_prompt, please_wait_message = load_channel_settings(channel_name, channel_id)
        print("Aplicando prompt padrão")

    print(f"Canal: {channel_name}, Thread TS: {thread_ts}, Prompt: {system_prompt}")

    bot_user_id = app.client.auth_test()["user_id"]
    conversation_history = construct_conversation_history(messages, bot_user_id, user_id, text, thread_ts, ts)
    status_message_ts = post_message_to_slack(channel_id, please_wait_message, thread_ts)
    
    def worker():
        try:
            response, _ = gpt(conversation_history, system_prompt, model="gpt-4o", max_tokens=4095, channel_id=channel_id, thread_ts=thread_ts)
            response = re.sub(r'```[a-zA-Z]+', '```', response)
            post_message_to_slack(channel_id, f"{response}", thread_ts)
        except Exception as e:
            print(f"Error from GPT-4: {e}")
        finally:
            if status_message_ts:
                delete_message_from_slack(channel_id, status_message_ts)
    
    threading.Thread(target=worker).start()

def extract_image_urls(text):
    pattern = r'https?://[^\s]+?(?:jpg|jpeg|png|gif)'
    urls = re.findall(pattern, text)
    return urls

def registro_uso(user_id, user_name, channel_name, current_time, user_message):
    fieldnames = ['user_id', 'user_name', 'channel_name', 'timestamp', 'user_message']
    try:
        with open('registro_uso.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow({
                'user_id': user_id,
                'user_name': user_name,
                'channel_name': channel_name,
                'timestamp': current_time,
                'user_message': user_message
            })
    except Exception as e:
        print(f"Erro ao escrever no arquivo CSV: {e}")

def gpt(conversation_history, system_prompt, channel_id, thread_ts=None, model="gpt-4o", max_tokens=4095, temperature=0.6):
    system_message = {
        "role": "system",
        "content": system_prompt
    }
    conversation_history_with_system_message = [system_message] + conversation_history
    tools_parameter = convert_functions_config_to_tools_parameter(functions_config) if functions_config else None
    request_payload = {
        "model": model,
        "messages": conversation_history_with_system_message,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if tools_parameter:
        request_payload["tools"] = tools_parameter
    response = client.chat.completions.create(**request_payload)
    answer = response.choices[0].message.content if response.choices[0].message.content else "No response content."
    return answer, None

def fetch_conversation_history(channel_id, thread_ts):
    try:
        history = app.client.conversations_replies(channel=channel_id, ts=thread_ts)
        return history['messages']
    except SlackApiError as e:
        print(f"Failed to fetch conversation history: {e}")
        if not handle_slack_api_error(e):
            raise
        return []

def handle_slack_api_error(e):
    if e.response["error"] in ["missing_scope", "not_in_channel"]:
        print(f"Slack API error due to missing permissions: {e.response['needed']}")
        return True 
    return False 

def determine_channel_and_user_names(channel_id, user_id):
    try:
        user_info = app.client.users_info(user=user_id)
        user_name = user_info['user']['real_name']
    except Exception as e:
        print(f"Error fetching user name: {e}")
        user_name = "Unknown User"
    
    try:
        channel_info = app.client.conversations_info(channel=channel_id)
        is_direct_message = channel_info['channel'].get('is_im', False)
        channel_name = "Direct Message" if is_direct_message else channel_info['channel']['name']
    except Exception as e:
        print(f"Error fetching channel name: {e}")
        channel_name = "Unknown Channel"

    return user_name, channel_name

def construct_conversation_history(messages, bot_user_id, user_id, current_text, thread_ts=None, ts=None):
    conversation_history = []
    for msg in messages:
        role = "user" if msg.get("user") == user_id else "assistant"
        content = msg.get("text")
        if content:
            conversation_history.append({"role": role, "content": content})
    if not thread_ts or thread_ts == ts:
        conversation_history.append({"role": "user", "content": current_text})
    return conversation_history

def post_message_to_slack(channel_id, text, thread_ts=None):
    if not text: 
        return None
    try:
        response = app.client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts
        )
        return response['ts'] 
    except Exception as e:
        print(f"Failed to post message to Slack: {e}")
        return None

def delete_message_from_slack(channel_id, ts):
    try:
        app.client.chat_delete(channel=channel_id, ts=ts)
    except Exception as e:
        print(f"Failed to delete message from Slack: {e}")

def ask_chatgpt_with_image(text, image_url, user_id, channel_id, thread_ts=None, ts=None):
    global client
    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]}
    ]
    print(f"Mensagens enviadas para a API: {messages}")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1024
        )
        answer = response.choices[0].message.content
        print("Resposta do GPT-4o:", answer)
        post_message_to_slack(channel_id, answer, thread_ts)
    except Exception as e:
        print(f"Erro ao chamar o GPT-4o: {e}")
        post_message_to_slack(channel_id, "Houve um erro ao processar sua imagem.", thread_ts)

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)
    event = body["event"]
    if 'subtype' not in event and 'user' in event:
        channel_id = event["channel"]
        text = event["text"]
        user_id = event["user"]
        ts = event.get("ts")
        thread_ts = event.get("thread_ts")
        
        image_urls = extract_image_urls(text)

        if image_urls:
            print(f"URLs de imagem encontradas: {image_urls}")
            ask_chatgpt_with_image(text, image_urls[0], user_id, channel_id, thread_ts, ts)
        else:
            if thread_ts and thread_ts != ts:
                thread_history = app.client.conversations_replies(
                    channel=channel_id,
                    ts=thread_ts
                )
                messages = thread_history['messages']
                bot_user_id = app.client.auth_test()["user_id"] 
                if any(f"<@{bot_user_id}>" in msg.get("text", "") for msg in messages if msg.get("ts") == thread_ts):
                    ask_chatgpt(text, user_id, channel_id, thread_ts, ts)
                elif event["channel_type"] == "im":
                    ask_chatgpt(text, user_id, channel_id, thread_ts, ts)
                else:
                    logger.info("Ignored event: bot was not @ mentioned in the original thread message")
            elif event["channel_type"] == "im":
                ask_chatgpt(text, user_id, channel_id, ts)
            else:
                logger.info("Ignored event: not a direct message or thread reply")
    else:
        logger.info("Ignored event: not a user message or has subtype")


@app.event("app_mention")
def handle_app_mention_events(body, logger):
    logger.info(body)
    event = body["event"]
    user_id = event["user"]
    text = event["text"]
    channel_id = event["channel"]
    ts = event.get("ts")
    thread_ts = event.get("thread_ts")
    if thread_ts:
        thread_history = app.client.conversations_replies(
            channel=channel_id,
            ts=thread_ts
        )
        messages = thread_history['messages']
        bot_user_id = app.client.auth_test()["user_id"] 
        if any(f"<@{bot_user_id}>" in msg.get("text", "") for msg in messages):
            ask_chatgpt(text, user_id, channel_id, thread_ts)
        else:
            logger.info("Ignored app_mention: bot was not @ mentioned in the thread")
    else:
        ask_chatgpt(text, user_id, channel_id, ts)

@app.command("/teste_menu")
def handle_menu_command(ack, body, client):
    ack()
    channel_id = body["channel_id"]
    menu_comandos(client, channel_id)

@app.action("button_1")
def handle_button_1_action(ack, body, client, context):
    handle_button_click(ack, body, client, context)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
