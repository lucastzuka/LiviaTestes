import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Tokens do Slack
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

# Inicializar o cliente do Slack
client = WebClient(token=SLACK_BOT_TOKEN)

def get_channel_id(channel_name):
    try:
        print("Fetching list of channels...")
        response = client.conversations_list(types="public_channel,private_channel")
        print("Channels fetched successfully.")
        for channel in response['channels']:
            print(f"Found channel: {channel['name']} with ID: {channel['id']}")
            if channel['name'] == channel_name:
                print(f"Channel {channel_name} found with ID: {channel['id']}")
                return channel['id']
        print(f"Channel {channel_name} not found.")
        return None
    except SlackApiError as e:
        print(f"Error fetching channels: {e.response['error']}")
        return None

def create_channel_canvas(channel_id, content):
    try:
        print("Creating channel canvas...")
        response = client.api_call(
            api_method='functions.channel_canvas_create',
            json={
                "channel_id": channel_id,
                "canvas_create_type": "blank",
                "content": content
            }
        )
        print("Channel canvas created successfully.")
        return response['canvas_id']
    except SlackApiError as e:
        print(f"Error creating channel canvas: {e.response['error']}")
        return None

if __name__ == "__main__":
    # Defina o título e o conteúdo do canvas
    title = "newsletter olá amigos"
    content = {
        "type": "rich_text",
        "elements": [
            {
                "type": "rich_text_section",
                "elements": [
                    {
                        "type": "text",
                        "text": "Olá amigos, esta é a nossa newsletter!"
                    }
                ]
            }
        ]
    }

    # Nome do canal onde o canvas será compartilhado
    channel_name = "random"

    # Obtenha o ID do canal a partir do nome
    print(f"Looking for channel: {channel_name}")
    channel_id = get_channel_id(channel_name)

    if channel_id:
        # Crie o canvas no canal
        print(f"Creating channel canvas in channel: {channel_name}")
        canvas_id = create_channel_canvas(channel_id, content)

        if canvas_id:
            print(f"Canvas created successfully with ID: {canvas_id}")
    else:
        print(f"Could not find the channel: {channel_name}. Please make sure the bot is added to the channel.")