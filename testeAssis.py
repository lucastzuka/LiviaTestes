
from openai import OpenAI 
import openai  
import time  # usada para esperar entre as verificações

OPENAI_API_KEY = "sk-proj-RFEYhMvLfqgFlpZ87UvXT3BlbkFJNRqzyFEOGxLexRil2tBV" 
ASSISTANT_ID = "asst_zloVW1yPnQYcYEhCF5qf7kFl"  # ID do Assistant que será usado

client = OpenAI(api_key=OPENAI_API_KEY)

# Função para criar uma nova thread da API de Assistants
def create_thread(client):
    thread = client.beta.threads.create()
    return thread.id  # Retorna o ID da thread criada

# Função para adicionar uma mensagem à thread
def add_message_to_thread(client, thread_id, role, content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role=role, 
        content=content
    )
    return message

# Função para iniciar a execução do assistente
def run_assistant(client, assistant_id, thread_id):
    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=thread_id
    )
    return run.id

# Função para aguardar a conclusão da execução do assistente
def wait_for_run_completion(client, thread_id, run_id):
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run_status.status == 'completed':
            return
        time.sleep(1)  # Espera 1 segundo antes de verificar novamente

# Função para obter a resposta do assistente
def get_assistant_response(client, thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value  # Retorna o texto da última mensagem

# Função principal que controla o fluxo da conversa
def main():
    thread_id = create_thread(client)  # Cria uma nova thread
    print("Digite 'sair' para terminar a conversa.")
    
    while True:
        user_input = input("Você: ")  # Recebe a entrada do usuário
        if user_input.lower() == "sair":
            break  # Sai do loop se o usuário digitar 'sair'

        # Adiciona a mensagem do usuário à thread
        add_message_to_thread(client, thread_id, "user", user_input)

        # Executa o assistente
        run_id = run_assistant(client, ASSISTANT_ID, thread_id)
        
        # Aguarda a conclusão da execução
        wait_for_run_completion(client, thread_id, run_id)
        
        # Obtém e exibe a resposta do assistente
        response = get_assistant_response(client, thread_id)
        print(f"Assistente: {response}")


if __name__ == "__main__":
    main()  