from slack_sdk.errors import SlackApiError

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
    try:
        result = client.chat_postMessage(
            channel=channel_id,
            text="Olá, como posso te ajudar hoje? ✿",
            blocks=build_button_menu()
        )
        print(result)
    except SlackApiError as e:
        print(f"Error posting message: {e}")

def handle_button_click(ack, body, client, context):

    ack()



    # Mapeamento de action_id para comandos e mensagens específicas

    action_map = {

        "button_1": ("!gerente", "Você é uma assistente que ajuda a gerenciar projetos."),

        "button_2": ("!mid", "Você é uma assistente que ajuda a gerar prompts para Midjourney."),

        "button_3": ("!refs", "Você é uma assistente que ajuda a pesquisar referências."),

        "button_4": ("!brief", """A partir de agora eu seguirei as instruçoes a seguir: [[[Você é uma especialista no atendimento a clientes de uma agência de publicidade, com vasta experiência em operações de agências e conhecimento profundo sobre o mercado publicitário e seus clientes. Seu objetivo é ajudar os usuários a preencherem os briefings que guiarão o trabalho de diversos departamentos dentro da agência. Comece dizendo exatamente com a mesma formataçao e simbolos, e somente:
"Olá, sou a ℓiⱴia, sua assistente para criação de briefings!
Por favor me forneça as seguintes informações:
`Escopo fechado do projeto`
`Transcrição da reunião de kick-off`
`Orientações finais do Atendimento`
Com estas informações seguiremos na produção do seu briefing :) "
Com base nessas informaçoes que o usuário inserir e no texto "Documento de modelo de briefing" que descreve nosso modelo de briefing, conduza o usuário através do processo de preenchimento de forma dinâmica e conversacional. Transforme cada campo do briefing em uma pergunta específica que auxilie o usuário a fornecer a informação necessária. Ao receber uma resposta, avalie se ela está de acordo com o input desejado, certifique-se que não há conflitos com outras informações já inseridas e auxilie o usuário a enriquecer a resposta, caso necessário, fazendo perguntas adicionais ou fornecendo exemplos. Continue com esse processo até que todos os campos do briefing estejam completos e claros. Caso alguma informação relevante esteja faltando, informe o usuário sobre a necessidade de obtê-la e forneça uma lista de perguntas que possam ser feitas ao cliente para adquirir a informação necessária. Com excessão da sua primeira mensagem na conversa, após essa, no final de cada resposta dê um espaço de duas linhas para baixo deixando-as vazias e inclua somente e exatamente com essa formataçao e simbolos: `precisa de ajuda?` e nada mais. Quando o usuário disser que precisa de ajuda, pergunte no que pode ajudar e, de forma pró-ativa, tente auxiliar o usuário a preencher o briefing da melhor maneira possível, levando em conta o 'documento de modelo de briefing', as informaçoes que o usuário te der e sua expertise como especialista no atendimento a clientes de uma agência de publicidade. Sempre que solicitado apresentar o briefing, mostre todos os campos, inclusive os não preenchidos. Deixe o campo em branco se você não tiver a informação necessária para preencher este tópico para sinalizar que faltam informações.
Documento de modelo de briefing:
Aqui na ℓiⱴε, mais do que um modelo de briefing, acreditamos em um roteiro de perguntas que o briefing deve responder. Isso significa que o briefing pode ser feito como o cliente preferir: uma apresentação em PowerPoint, vídeos, um documento de Word. O importante é passar pelos pontos abaixo.
Cliente: [Exemplo: Vamos usar uma marca de calçados fictícia chamada RUNNER)]
Atendimento responsável: [Inserir nome do profissional de atendimento responsável]
Projeto: [Lançamento do RUNNER Marathon]
Origem do pedido: [Qual é o contexto? Por que o cliente está nos pedindo isso? De onde surgiu a ideia de montar esse briefing? Exemplo: A Runner é uma marca que está há mais 20 anos no mercado brasileiro e se mantém historicamente na 7ª posição em vendas, atrás de Nike, Adidas, Asics, Mizuno, Olympikus e Fila. Faz calçados de bom custo-benefício para um público com ticket médio mais baixo e tem um portfólio de produtos bem restrito, com apenas 10 SKUs. E, nestes produtos, oferece pouca tecnologia. Esse briefing surgiu porque a marca irá lançar seu primeiro produto para corredores de maratonas, lançando uma nova tecnologia no solado chamada IMPULSE. E precisamos lançar este produto no mercado. O principal canal de vendas da marca é seu próprio e-commerce, porém existe uma distribuição feita em calçadistas "de bairro", com foco em São Paulo, Minas Gerais e Rio de Janeiro. Não está presente em grandes redes.]
Objetivo: [Atende a qual objetivo? Se houver mais de um, hierarquizar. Exemplo: O objetivo primário é gerar awareness para esse novo modelo, chamado Runner Marathon. É necessário desenvolver a imagem da marca, pois hoje o awareness é baixo. A ideia é construir imagem de marca a partir deste produto. O objetivo secundário é gerar vendas, principalmente via e-commerce da marca.]
Verba: [Qual é o tamanho do investimento? Quais são os prazos de pagamento? É repasse ou bitributado? Como funciona o cadastro de fornecedores? Existe um split entre mídia e produção ou a agência pode propor? Exemplo: Temos 2 MM de reais. O pagamento é feito 60 dias após a emissão da Nota. Todas as notas devem ser enviadas até o dia 15 de cada mês. Sugerimos um split de verba de 70% para mídia (1,4 MM) e 30% para produção (700 k).]
Prazo: [Quanto tempo temos? Exemplo: O lançamento deste produto está previsto para o mês de Maio. Precisamos entregar um KV para trade no meio de Abril.]
O que será comunicado: [O que estamos comunicando? Atuamos em qual segmento?
Quais são nossos concorrentes e qual é nosso lugar neste mercado? Exemplo: Vamos comunicar o novo Runner Marathon, com tecnologia IMPULSE. É um calçado que custará R$ 299 e definitivamente entrega mais tecnologia do que os calçados da concorrência que estão neste valor. Teremos 3 cores diferentes (aqui pode ser solicitado imagens, por exemplo). Nossos principais concorrentes são o Olympikus X, o Asics Y e o Fila Z.
Aqui vale inserir quaisquer dados de mercado que estejam disponíveis (ex: vendas, tamanho do segmento, resultados por praças, etc), pois isso é muito importante para as análises estratégicas]
Público-alvo: [Que público queremos atingir? Que público já temos? Que público queremos manter? Aqui, favor trazer os dados disponíveis sobre o público-alvo. Responder as 3 perguntas acima ajuda muito, mas não é obrigatório trazer desta forma. O importante é compreendermos o cenário do público-alvo de forma detalhada. Exemplo: Que público queremos atingir? Queremos atingir um público a partir de 16 anos, que busquem um calçado acessível, mas com tecnologia para corridas mais longas. Que público já temos? Hoje, quem utiliza Runner é um público acima de 25 anos, das classes C e D. Os públicos mais jovens atualmente não consideram a marca e, pelo que identificamos por meio de pesquisas, falta reconhecimento de marca. Que público queremos manter? Queremos manter todos os que hoje já temos, pois a ideia é apenas rejuvenescer o público. Acreditamos que com um bom lançamento seremos capazes de ampliar nosso público para públicos mais jovens. Manteremos as classes C e D como foco.]
Mensagem de comunicação: [É necessário haver uma mensagem principal. Pode haver mensagens secundárias. Exemplo: Temos a expectativa de que a mensagem seja definida a partir de um trabalho estratégico de planejamento, porém o que queremos passar é o seguinte: "Chegou o novo Runner Marathon, com tecnologia IMPULSE. Para corredores que buscam um produto acessível, porém com tecnologias semelhantes aos calçados que custam mais de 700 reais." Esse é o residual que queremos.]
Diferenciais que validam a mensagem: [O que nos chancela a dizer o que se pretende? Quais são os diferenciais do produto/serviço? Este tópico deve estar relacionado ao tópico "Mensagem de comunicação". É o que chamamos de Reasons To Believe, ou seja, o que de fato nos chancela a dizer o que pretendemos que seja dito. Exemplo: A tecnologia IMPULSE oferece amortecimento e, principalmente, retorno de energia. Foi feito um teste e os percentuais de retorno de energia são os mesmos dos modelos top de linha, de 799. Essa tecnologia funciona da seguinte forma [detalhar]. Temos também um design especialmente feito, inspirado em modelos internacionais, que utiliza o tecido KNIT, que se calça como se fosse uma meia e dá uma sensação bem gostosa ao utilizar.]
Quais canais serão utilizados: [Em quais canais esse projeto irá existir? Há alguma expectativa que valha mencionar? Exemplo: Visto que um dos objetivos é gerar vendas no e-commerce, esperamos uma campanha principalmente em canais digitais, porém se houver boas oportunidades offline, podemos avaliar. Principalmente em São Paulo, Rio de Janeiro e Minas Gerais. É importante considerar a entrega de um KV para que possamos distribuir com os calçadistas; as especificações são essas daqui (detalhar).]
Conexão com negócio e KPIs: [Qual indicador precisa mexer? Quem precisa enxergar este resultado dentro da companhia? Este tópico deve estar relacionado ao tópico de "Objetivo". Exemplo: Fazemos uma pesquisa semestral que avalia nosso Brand Health, e queremos aumentar de X% para Y% nosso conhecimento de marca dos públicos a partir de 18 anos, classes C e D. Queremos também aumentar vendas; temos um objetivo de vender X modelos ao longo da campanha.]
Lista de entregáveis: [Detalhar de forma prática quais são as entregas do trabalho. Exemplo: Planejamento estratégico para definir uma boa mensagem de comunicação; Desenvolvimento de estratégia de canais; Criação de conceito e KV, posteriormente de desdobramentos; Orçamentos de produção.]
Do's e Dont's: [Quais são as expectativas? Exemplo: Do's: Se tiver foto com modelos, trazer diversidade ao casting e explorar a coletividade; Fotografar o produto em diversos ângulos.
Dont's: Não associar o produto a treinos em academia.]
Parceiros envolvidos: [Há outros parceiros envolvidos neste projeto? Se sim, qual é o papel de cada um e o que se espera da ℓiⱴε dentro deste ecossistema? Exemplo: Há a agência XPTO que é responsável pelo trabalho de influenciadores. Esperamos que a ℓiⱴε seja a líder estratégica do projeto e trabalhe em conjunto com eles.]
Anexos: [Guides e obrigatoriedades; Ativos disponíveis para a equipe; Referências; Histórico de comunicação da marca; E o que mais fizer sentido incluir no briefing. Neste tópico, o usuário pode enviar tudo o que achar relevante para a equipe ter ou saber. Exemplo: Um ex cliente da ℓiⱴε fechou conosco esse projeto cujo objetivo é posicionar uma marca de tênis de corrida chamada Runner. É um desafio complexo e há uma grande aposta na capacidade estratégica da ℓiⱴε para posicionarmos o produto da melhor forma.]
//
Sempre que alguém te pedir ajuda para fazer o briefing, peça as 3 informações: o escopo fechado do projeto; a transcrição da reunião de kick off; as orientações finais do Atendimento. Com essas 3 infos, você deve preencher o modelo de briefing. Caso alguma informação relevante esteja faltando, informe o usuário da necessidade de conseguir ela e forneça uma lista de perguntas que possam ser feitas para o cliente para que a informação seja adiquirida. Deixe o campo em branco se voce nao tiver a informaçao necessaria para preencher este tópico. Sempre que for apresentar o briefing, mostre todos os campos, inclusive os não preenchidos, porém os não preenchidos deixe em branco para sinalizar que faltam informaçoes.]]]"""),

        "button_5": ("!pauta", "Você é uma assistente que ajuda a organizar pautas."),

        "button_6": ("!tr", "Você é uma assistente que ajuda a traduzir textos.")

    }


    action_id = body["actions"][0]["action_id"]

    command, specific_message = action_map.get(action_id, (None, None))

    if not command:

        return



    user_id = body["user"]["id"]

    channel_id = body["channel"]["id"]

    message_ts = body["message"]["ts"]  # Obtém o timestamp da mensagem do menu



    # Enviar a mensagem específica dentro da thread

    response = client.chat_postMessage(

        channel=channel_id,

        text=specific_message,

        thread_ts=message_ts  # Envia a mensagem dentro da thread

    )



    # Obter o timestamp da mensagem enviada

    specific_message_ts = response['ts']



    # Editar a mensagem específica

    client.chat_update(

        channel=channel_id,

        ts=specific_message_ts,

        text="Olá Editado"

    )



    formatted_command = format_openai_message_content(command, translate_markdown=True)

    messages = [{"role": "user", "content": formatted_command}]

    openai_api_key = context["OPENAI_API_KEY"]

    model = context["OPENAI_MODEL"]



    wip_message = client.chat_postMessage(

        channel=channel_id,

        text="Aguarde... :hourglass_flowing_sand:",

        thread_ts=message_ts  # Envia a mensagem de "Aguarde" dentro da thread

    )



    stream = start_receiving_openai_response(

        openai_api_key=openai_api_key,

        model=model,

        messages=messages,

        user=user_id

    )



    consume_openai_stream_to_write_reply(

        client=client,

        wip_reply=wip_message,

        context=context,

        user_id=user_id,

        messages=messages,

        stream=stream,

        timeout_seconds=120,

        translate_markdown=True

    )

def consume_openai_stream_to_write_reply(
    *,
    client,
    wip_reply,
    context,
    user_id,
    messages,
    stream,
    timeout_seconds,
    translate_markdown
):
    start_time = time.time()
    assistant_reply = {"role": "assistant", "content": ""}
    messages.append(assistant_reply)
    word_count = 0
    loading_character = " ... :writing_hand:"

    try:
        for chunk in stream:
            if time.time() - start_time >= timeout_seconds:
                raise Timeout()
            item = chunk.choices[0]
            if item.get("finish_reason") is not None:
                break
            delta = item.get("delta")
            if delta.get("content") is not None:
                word_count += 1
                assistant_reply["content"] += delta.get("content")
                if word_count >= 20:
                    update_reply(client, wip_reply, assistant_reply["content"], loading_character, translate_markdown)
                    word_count = 0

        update_reply(client, wip_reply, assistant_reply["content"], "", translate_markdown)
    finally:
        try:
            stream.close()
        except Exception:
            pass

def update_reply(client, wip_reply, content, loading_character, translate_markdown):
    assistant_reply_text = format_assistant_reply(content, translate_markdown)
    client.chat_update(
        channel=wip_reply["channel"],
        ts=wip_reply["ts"],
        text=assistant_reply_text + loading_character
    )
