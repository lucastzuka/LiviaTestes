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
from caixa_de_duvidas_refresh import create_sheets_client, insert_data_into_sheet
from comandos import menu_comandos, handle_button_click

# Configuração de logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger('slack_bolt').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)

# Carregar variáveis de ambiente
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicialização do app e cliente OpenAI
app = App(token=SLACK_BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Carregar configuração de canais
def load_channel_config():
    try:
        with open('channel_config.json', 'r') as config_file:
            return json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Invalid or missing channel_config.json. Using default configuration.")
        return {}

channel_config = load_channel_config()

# Carregar configuração de funções
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
    
    registro_uso(user_id, user_name, channel_name, current_time, text)
    
    # Passe tanto channel_name quanto channel_id
    system_prompt, please_wait_message = load_channel_settings(channel_name, channel_id)
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

def load_channel_settings(channel_name, channel_id):
    if channel_id == 'C059NNLU3E1':  # ID do canal 'testes'
        system_prompt = "A partir de agora seu nome é Briefinzinho"
        please_wait_message = ":hourglass_flowing_sand: Aguarde..."
    else:
        channel_settings = channel_config.get(channel_name, {})
        system_prompt = channel_settings.get(
            "system_prompt",
            channel_config.get("system_prompt", "Você é a ℓiⱴia, uma assistente de inteligência artificial, jovem, alternativa e muito bem humorada")
        )
        please_wait_message = channel_settings.get(
            "please_wait_message",
            channel_config.get("please_wait_message", ":hourglass_flowing_sand: Aguarde...")
        )
    return system_prompt, please_wait_message

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
        print("No text to post to Slack.")
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

def process_file(file_id, user_id, channel_id):
    try:
        file_info = app.client.files_info(file=file_id)
        file_url = file_info["file"]["url_private"]
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        response = requests.get(file_url, headers=headers)
        if response.status_code == 200:
            file_content = response.content
            ask_chatgpt_with_image("Imagem enviada pelo usuário", file_url, user_id, channel_id)
        else:
            print(f"Erro ao baixar o arquivo: {response.status_code}")
    except SlackApiError as e:
        print(f"Erro ao obter informações do arquivo: {e.response['error']}")

def extract_image_urls(text):
    pattern = r'https?://[^\s]+?(?:jpg|jpeg|png|gif)'
    urls = re.findall(pattern, text)
    print(f"URLs extraídas: {urls}")
    return urls

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

@app.event("file_shared")
def handle_file_shared_events(body, logger):
    logger.info(body)
    event = body["event"]
    file_id = event["file"]["id"]
    user_id = event["user_id"]
    channel_id = event["channel_id"]
    process_file(file_id, user_id, channel_id)

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

@app.action("plain_text_input-action")
def handle_some_action(ack, body, logger):
    ack()  
    user_input = body['actions'][0]['value']
    print(f"Nova duvida na News: {user_input}")  
    insert_data_into_sheet([[user_input]])
    logger.info(f"Dados inseridos na planilha: {user_input}")

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

@app.event("app_home_opened")
def app_home_opened(ack, event, logger):
    ack()
    logger.info(event)
    user_id = event["user"]
    response = app.client.chat_postMessage(
        channel=user_id,
        text=f"Olá! Bem-vindo ao Slack. Como posso ajudá-lo hoje?"
    )
    logger.info(response)

@app.command("/menu")
def handle_menu_command(ack, body, client):
    ack()
    channel_id = body["channel_id"]
    menu_comandos(client, channel_id)

@app.action("button_1")
@app.action("button_2")
@app.action("button_3")
@app.action("button_4")
@app.action("button_5")
@app.action("button_6")
def handle_button_actions(ack, body, client, context):
    handle_button_click(ack, body, client, context)

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

def convert_functions_config_to_tools_parameter(functions_config):
    tools = []
    for func in functions_config:
        tool_def = {
            "type": "function",
            "function": {
                "name": func["name"],
                "description": func.get("description", ""),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }
        for param_name, param_type in func.get("parameters", {}).items():
            tool_def["function"]["parameters"]["properties"][param_name] = {
                "type": param_type,
                "description": f"The {param_name}",
            }
            tool_def["function"]["parameters"]["required"].append(param_name)
        tools.append(tool_def)
    return tools

def handle_function_call(function_name, arguments, channel_id, thread_ts=None, conversation_history={}, model="gpt-4o"):
    for func in functions_config:
        if func["name"] == function_name:
            helper_program_path = func.get("helper_program")
            break
    else:
        print(f"No helper program configured for function: {function_name}")
        return "No helper program configured for this function.", None

    if not helper_program_path:
        return "Helper program path not found.", None

    arguments_str = json.dumps(arguments)
    conversation_str = json.dumps(conversation_history)
    status_message = f'Asking "{function_name}": "{arguments["question"]}" with {model}'
    status_ts = post_message_to_slack(channel_id, status_message, thread_ts)
    base_dir = os.path.dirname(helper_program_path)
    venv_python_path = os.path.join(base_dir, '.venv', 'bin', 'python')
    command = [helper_program_path] if not os.path.exists(venv_python_path) else [venv_python_path, helper_program_path]
    command += [function_name, arguments_str, conversation_str, model]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, env=os.environ.copy())
        output = result.stdout
        print("Helper program output:", output)
        return output, status_ts
    except subprocess.CalledProcessError as e:
        print("Helper program failed with error:", e.stderr)
        error_message = f"Error executing the helper program: {e.stderr}"
        return error_message, status_ts
    except Exception as e:
        print(f"Unexpected error when calling helper program: {e}")
        error_message = "Unexpected error when executing the helper program."
        return error_message, status_ts

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
