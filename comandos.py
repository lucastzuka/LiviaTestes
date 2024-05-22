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

        "button_4": ("!brief", """A partir de agora seu nome é NBriefinzinho"""),

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
