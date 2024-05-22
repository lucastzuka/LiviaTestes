from slack_sdk.errors import SlackApiError



def build_button_menu():

    buttons = [

        {

            "type": "button",

            "text": {

                "type": "plain_text",

                "text": "Gerente"

            },

            "value": "!gerente",

            "action_id": "button_1"

        },

        {

            "type": "button",

            "text": {

                "type": "plain_text",

                "text": "Midjourney"

            },

            "value": "!mid",

            "action_id": "button_2"

        },

        {

            "type": "button",

            "text": {

                "type": "plain_text",

                "text": "Refs"

            },

            "value": "!refs",

            "action_id": "button_3"

        },

        {

            "type": "button",

            "text": {

                "type": "plain_text",

                "text": "Briefing"

            },

            "value": "!brief",

            "action_id": "button_4"

        },

        {

            "type": "button",

            "text": {

                "type": "plain_text",

                "text": "Pauta"

            },

            "value": "!pauta",

            "action_id": "button_5"

        },

        {

            "type": "button",

            "text": {

                "type": "plain_text",

                "text": "Tradutor"

            },

            "value": "!tr",

            "action_id": "button_6"

        }

    ]



    for button in buttons:

        button['style'] = 'primary'



    descriptions = """𝗚𝗲𝗿𝗲𝗻𝘁𝗲: Gerencie seu projeto

𝗠𝗶𝗱: Gerador de prompts para Midjourney

𝗥𝗲𝗳𝘀: Pesquisa de referencias

𝗕𝗿𝗶𝗲𝗳: Criador de briefing

𝗣𝗮𝘂𝘁𝗮: Organizador de Pauta

𝗧𝗿𝗮𝗱𝘂𝘁𝗼𝗿: Tradutor de textos"""



    intro_section = {

        "type": "section",

        "text": {

            "type": "mrkdwn",

            "text": """*Olá, como posso te ajudar hoje? ✿*"""

        }

    }



    button_section = {

        "type": "actions",

        "elements": buttons

    }



    sections = [intro_section, button_section]

    divider_section = {"type": "divider"}

    sections.append(divider_section)



    context_section = {

        "type": "context",

        "elements": [

            {

                "type": "plain_text",

                "text": descriptions,

                "emoji": True

            }

        ]

    }

    sections.append(context_section)



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

    action_id = body["actions"][0]["action_id"]

    user_id = body["user"]["id"]

    channel_id = body["channel"]["id"]



    if action_id == "button_1":

        command = "!gerente"

    elif action_id == "button_2":

        command = "!mid"

    elif action_id == "button_3":  

        command = "!refs"

    elif action_id == "button_4":  

        command = "!brief"

    elif action_id == "button_5":  

        command = "!pauta"

    elif action_id == "button_6":  

        command = "!tr"

    else:

        return



    formatted_command = format_openai_message_content(command, translate_markdown=True)

    messages = [{"role": "user", "content": formatted_command}]

    openai_api_key = context["OPENAI_API_KEY"]

    model = context["OPENAI_MODEL"]



    wip_message = client.chat_postMessage(

        channel=channel_id,

        text="Aguarde... :hourglass_flowing_sand:"

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

    translate_markdown,

):

    start_time = time.time()

    assistant_reply = {"role": "assistant", "content": ""}

    messages.append(assistant_reply)

    word_count = 0

    try:

        loading_character = " ... :writing_hand:"

        for chunk in stream:

            spent_seconds = time.time() - start_time

            if timeout_seconds < spent_seconds:

                raise Timeout()

            item = chunk.choices[0]

            if item.get("finish_reason") is not None:

                break

            delta = item.get("delta")

            if delta.get("content") is not None:

                word_count += 1

                assistant_reply["content"] += delta.get("content")

                if word_count >= 20:

                    assistant_reply_text = format_assistant_reply(

                        assistant_reply["content"], translate_markdown

                    )

                    client.chat_update(

                        channel=wip_reply["channel"],

                        ts=wip_reply["ts"],

                        text=assistant_reply_text + loading_character

                    )

                    word_count = 0



        assistant_reply_text = format_assistant_reply(

            assistant_reply["content"], translate_markdown

        )

        client.chat_update(

            channel=wip_reply["channel"],

            ts=wip_reply["ts"],

            text=assistant_reply_text

        )

    finally:

        try:

            stream.close()

        except Exception:

            pass

