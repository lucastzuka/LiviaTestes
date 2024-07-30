# liviatestes.py
import os
import re
import json
import csv
import logging
import threading
from datetime import datetime
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from openai import OpenAI
from comandos import menu_comandos, handle_button_click
from globals_manager import test_set_thread_ts, test_get_thread_ts

# Configuração de logging
logging.basicConfig(level=logging.WARNING)
for logger_name in ['slack_bolt', 'httpx', 'openai']:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Carregamento de variáveis de ambiente
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicialização da app Slack e cliente OpenAI
app = App(token=SLACK_BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Prompts do sistema
SYSTEM_PROMPT_PERSONALIZADO = """Você é uma especialista no atendimento a clientes e seu nome é AtendCli"""
SYSTEM_PROMPT_PADRAO = """Você é a ℓiⱴia, uma assistente de inteligência artificial, jovem, alternativa e muito bem humorada"""

# Funções de carregamento de configurações
def load_json_config(filename, default=None):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Arquivo {filename} inválido ou ausente. Usando configuração padrão.")
        return default or {}

channel_config = load_json_config('channel_config.json')
functions_config = load_json_config('functions.json', [])

def load_channel_settings(channel_name, channel_id): 
    channel_settings = channel_config.get(channel_name, {})
    system_prompt = channel_settings.get("system_prompt", channel_config.get("system_prompt", SYSTEM_PROMPT_PADRAO))
    please_wait_message = channel_settings.get("please_wait_message", channel_config.get("please_wait_message", ":hourglass_flowing_sand: Aguarde..."))
    
    return system_prompt, please_wait_message

# Função principal de interação com o ChatGPT
def ask_chatgpt(text, user_id, channel_id, thread_ts=None, ts=None):
    
    # Busca o histórico da conversa se estiver em uma thread
    messages = fetch_conversation_history(channel_id, thread_ts) if thread_ts else []
    
    # Determina o nome do usuário e do canal
    user_name, channel_name = determine_channel_and_user_names(channel_id, user_id)
    
    # Registra o uso da função
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    registro_uso(user_id, user_name, channel_name, current_time, text)
    
    # Carrega as configurações do canal
    if thread_ts and thread_ts == test_get_thread_ts():
        system_prompt, please_wait_message = SYSTEM_PROMPT_PERSONALIZADO, ":hourglass_flowing_sand: Aguarde..."
        print("Aplicando prompt personalizado para a thread")
    else:
        system_prompt, please_wait_message = load_channel_settings(channel_name, channel_id)
        print("Aplicando prompt padrão")

    print(f"Canal: {channel_name}, Thread TS: {thread_ts}, Prompt: {system_prompt}")

    # Constrói o histórico da conversa
    bot_user_id = app.client.auth_test()["user_id"]
    conversation_history = construct_conversation_history(messages, bot_user_id, user_id, text, thread_ts, ts)
    
    # Posta uma mensagem de espera no Slack
    status_message_ts = post_message_to_slack(channel_id, please_wait_message, thread_ts)
    
    # Inicia uma thread para processar a resposta do GPT
    def worker():
        try:
            response, _ = gpt(conversation_history, system_prompt, model="gpt-4o", max_tokens=4095, channel_id=channel_id, thread_ts=thread_ts)
            response = re.sub(r'```[a-zA-Z]+', '```', response)
            post_message_to_slack(channel_id, response, thread_ts)
        except Exception as e:
            print(f"Erro do GPT-4: {e}")
        finally:
            if status_message_ts:
                delete_message_from_slack(channel_id, status_message_ts)
    
    threading.Thread(target=worker).start()

# Função para registro de uso
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

# Função para interação com o modelo GPT
def gpt(conversation_history, system_prompt, channel_id, thread_ts=None, model="gpt-4o", max_tokens=4095, temperature=0.6):
    system_message = {"role": "system", "content": system_prompt}
    conversation_history_with_system_message = [system_message] + conversation_history
    
    request_payload = {
        "model": model,
        "messages": conversation_history_with_system_message,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    if functions_config:
        request_payload["tools"] = convert_functions_config_to_tools_parameter(functions_config)
    
    response = client.chat.completions.create(**request_payload)
    answer = response.choices[0].message.content if response.choices[0].message.content else "Sem conteúdo na resposta."
    return answer, None

# Funções auxiliares para interação com o Slack
def fetch_conversation_history(channel_id, thread_ts):
    try:
        history = app.client.conversations_replies(channel=channel_id, ts=thread_ts)
        return history['messages']
    except SlackApiError as e:
        print(f"Falha ao buscar histórico da conversa: {e}")
        if not handle_slack_api_error(e):
            raise
        return []

def handle_slack_api_error(e):
    if e.response["error"] in ["missing_scope", "not_in_channel"]:
        print(f"Erro da API do Slack devido a permissões ausentes: {e.response['needed']}")
        return True 
    return False 

def determine_channel_and_user_names(channel_id, user_id):
    try:
        user_info = app.client.users_info(user=user_id)
        user_name = user_info['user']['real_name']
    except Exception as e:
        print(f"Erro ao buscar nome do usuário: {e}")
        user_name = "Usuário Desconhecido"
    
    try:
        channel_info = app.client.conversations_info(channel=channel_id)
        is_direct_message = channel_info['channel'].get('is_im', False)
        channel_name = "Mensagem Direta" if is_direct_message else channel_info['channel']['name']
    except Exception as e:
        print(f"Erro ao buscar nome do canal: {e}")
        channel_name = "Canal Desconhecido"

    return user_name, channel_name

def construct_conversation_history(messages, bot_user_id, user_id, current_text, thread_ts=None, ts=None):
    conversation_history = [
        {"role": "user" if msg.get("user") == user_id else "assistant", "content": msg.get("text")}
        for msg in messages if msg.get("text")
    ]
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
        print(f"Falha ao postar mensagem no Slack: {e}")
        return None

def delete_message_from_slack(channel_id, ts):
    try:
        app.client.chat_delete(channel=channel_id, ts=ts)
    except Exception as e:
        print(f"Falha ao deletar mensagem do Slack: {e}")

# Event handlers do Slack
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
        
        if thread_ts and thread_ts != ts:
            thread_history = app.client.conversations_replies(channel=channel_id, ts=thread_ts)
            messages = thread_history['messages']
            bot_user_id = app.client.auth_test()["user_id"] 
            if any(f"<@{bot_user_id}>" in msg.get("text", "") for msg in messages if msg.get("ts") == thread_ts):
                ask_chatgpt(text, user_id, channel_id, thread_ts, ts)
            elif event["channel_type"] == "im":
                ask_chatgpt(text, user_id, channel_id, thread_ts, ts)
            else:
                logger.info("Evento ignorado: bot não foi mencionado na mensagem original da thread")
        elif event["channel_type"] == "im":
            ask_chatgpt(text, user_id, channel_id, ts)
        else:
            logger.info("Evento ignorado: não é uma mensagem direta ou resposta de thread")
    else:
        logger.info("Evento ignorado: não é uma mensagem de usuário ou tem subtipo")

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
        thread_history = app.client.conversations_replies(channel=channel_id, ts=thread_ts)
        messages = thread_history['messages']
        bot_user_id = app.client.auth_test()["user_id"] 
        if any(f"<@{bot_user_id}>" in msg.get("text", "") for msg in messages):
            ask_chatgpt(text, user_id, channel_id, thread_ts)
        else:
            logger.info("Menção de app ignorada: bot não foi mencionado na thread")
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

# Inicialização da aplicação
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()