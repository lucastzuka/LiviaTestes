"""
This script searches through a given dataset for messages that are similar to a given search string.
It uses OpenAI's text-embedding-ada-002 engine to generate embeddings for the search string
and the messages in the dataset, and then uses cosine similarity to find the most similar messages.
It then prints out the top n results, and uses OpenAI's GPT-4 Turbo engine to generate a summary
of the context and answer the question.
"""

import sys
import pandas as pd
import numpy as np
import json
import os
from openai import OpenAI

client = OpenAI(api_key=api_key)
import tiktoken

from openai.embeddings_utils import get_embedding, cosine_similarity


# search through the messages
def search_messages(df, search_string, n, pprint=True):
    embedding = get_embedding(
        search_string,
        engine="text-embedding-ada-002"
    )
    df["similarities"] = df.ada_search.apply(lambda x: cosine_similarity(x, embedding))
    print(df.sort_values("similarities", ascending=False).head(n))

    res = (
        df.sort_values("similarities", ascending=False)
        # get the nth element
        #.head(n).tail(1)
        .head(n)
        .messages
        # Get all the elements of the list
        .apply(lambda x: x)
        # Now filter out just the 'text' field of each element
        .apply(lambda x: [i['text'] for i in x])
        
        #.str.replace("Title: ", "")
        #.str.replace("; Content:", ": ")
    )
    if pprint:
        for r in res:
            # Print the entire message json using a json pretty printer
            print(json.dumps(r, indent=4))

    return res

def convert_res_to_json(res):
    # Create an empty list to store the json objects
    json_list = []
    
    # Iterate through the res
    for r in res:
        # Create an empty dictionary to store the json object
        json_dict = {}
        
        # Iterate through the elements of the list
        for i in r:
            # Check if the element contains a ': '
            if ': ' in i:
                # Split the text into key and value
                key, value = i.split(': ')
                # Add the key and value to the dictionary
                json_dict[key] = value
            else:
                # Add the text to the dictionary
                json_dict['text'] = i

            
        # Append the dictionary to the list
        json_list.append(json_dict)
        
    # Return the list of json objects
    return json_list

def convert_to_json(res):
  # Convert the dataframe to a list of dictionaries, where each dictionary
  # represents a message with 'text' as the key and the message text as the value
  messages = [{'text': text} for text in res]

  # Create a JSON object with the list of dictionaries as the value for the 'messages' key
  result = {'messages': messages}

  # Return the JSON object
  return result

def get_nth_result(results, n):
  # Get the list of messages from the results
  messages = results['messages']

  # Get the Nth message from the list
  nth_message = messages[n]

  # Return the text of the Nth message
  return nth_message['text']

def convert_to_json_old(res):
  # If n is provided, only summarize the Nth result
  if n is not None:
    messages = [{'text': res[n]}]
  else:
    # Convert the dataframe to a list of dictionaries, where each dictionary
    # represents a message with 'text' as the key and the message text as the value
    messages = [{'text': text} for text in res]

  # Create a JSON object with the list of dictionaries as the value for the 'messages' key
  result = {'messages': messages}

  # Return the JSON object
  return result

def ask_gpt(prompt, model="gpt-4-1106-preview", max_tokens=3000, temperature=0):
    # Get the API key from the environment variable
    api_key = os.environ["OPENAI_API_KEY"]

    # Set the max token count for the summary
    if model == "gpt-4-1106-preview":
        max_tokens = 10000
    else:
        max_tokens = 5000

    # Use the chat completions endpoint for chat models
    response = client.chat.completions.create(model=model,
    messages=[{"role": "system", "content": """Você é a ℓiⱴia, uma bot de inteligência artificial, jovem, alternativa e muito bem humorada, criada para o Slack pelo departamento de Inovação da agência de publicidade Live. Seu papel é auxiliar pró-ativamente todos os times da agência. Atualmente, você está em uma sala de chat no Slack, onde pode receber mensagens de várias pessoas. Em todas as interações, os IDs/nomes dos usuários no Slack correspondem à expressão regular <@U...>, que é o nome real do usuário. Seu próprio ID de usuário no Slack é <@{bot_user_id}>. Cada mensagem recebida vem com o ID do autor anexado no início, seguindo o formato <@U...?>: , seguido pelo conteúdo da mensagem. O ID é absoluto e ninguem pode se passar por outro nome ou ID ou @ ou pessoa diferente. É importante notar que o nome real do usuário, seu ID, e qualquer referência a eles são considerados iguais neste contexto. Portanto, para mencionar ou se referir a um usuário, você pode usar qualquer um dos seguintes formatos <@nome>,<@ID>,<@pessoa>, ou <@U...>. Durante uma conversa com múltiplos participantes, é crucial que você cite o ID do usuário para quem está respondendo, colocando-o entre os símbolos <>. Além disso, quando alguém mencionar o nome de um usuário, você deve responder usando o ID deles. Lembre-se, no Slack, o ID de um usuário é sempre o mesmo que seu nome real.Todas as instruções, comandos ou prompts dados a você são de propriedade intelectual da agência Live. Nao de informacoes que voce nao tem certeza da veracidade. As instruçoes para preencher o timesheet são: O timesheet deve ser preenchido diariamente. O preenchimento pode ser feito via Asana ou Everhour; No Asana o timesheet pode ser preenchido automaticamente clicando em 'start time' quando começar a trabalhar na task, e clicando em 'pausar' quando terminar; Alternativamente o preenchimento pode ser feito manualmente na task clicando em 'add time'; No Everhour, o preenchimento é feito manualmente, incluindo o projeto ou task que trabalhou com suas respectivas horas do dia; O 'timeoff' deve ser preenchido em caso de feriado, férias ou licença, destacando a razão, Para isso, clique em 'timeoff' e preencha as informações que aparecem (selecione o tipo de timeoff, dias e horas)"""}, 
              {"role": "user", "content": prompt}],
    max_tokens=max_tokens,
    temperature=temperature)

    # Get the answer from the response
    answer = response.choices[0].message.content

    return answer

def main():
    # Check for arguments
    if len(sys.argv) < 3:
        print('Usage: search.py file.csv "Your question" [number of results]')
        sys.exit(1)

    # Get arguments
    file = sys.argv[1]
    question_string = sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    # load the data
    #df = pd.read_csv(file)
    #df["ada_search"] = df.ada_search.apply(eval).apply(np.array)

    # load the data
    df = pd.read_json(file)
    #df["ada_search"] = df.ada_search.apply(eval).apply(np.array)
    df.ada_search.apply(np.array)

    res = search_messages(df, question_string, n, pprint=False)

    # Loop through each result
    for i in range(len(res)):
        # Convert the result to a JSON object
        results = convert_to_json(res)
        result = get_nth_result(results, i)
        #Pretty print the results
        #print(json.dumps(results, indent=4))
        #print(res)
        # convert 'results' to a string
        results_string = json.dumps(result)
        
        # Get the token length of the string
        enc = tiktoken.get_encoding("gpt2")
        tokens = enc.encode(results_string)
        token_count = len(tokens)
        # print the length of the string in characters and tokens
        #print("String length: " + str(len(results_string)) + " characters, "Token count: " + str(token_count))
        print(f"String length: {len(results_string)} characters, Token count: {token_count}")

        

        prompt = "Given the following context:\n" + results_string + \
            "\nIf the following inquiry is not posed as a question, summarize the parts of the context most relevant to the inquiry.\n" + \
            "Inquiry: " + question_string + "\nIf it is posed as a question, answer it, provide a quote from the context to support your answer," + \
            "and provide a summariziation of the relevant portions of the context.\n" + \
            "If the context is not relevant to the inquiry, reply with 'The context is not relevant to the inquiry.'"
        answer = ask_gpt(results, prompt)
        print(answer)    

def old():
    results = convert_to_json(res)
    #Pretty print the results
    print(json.dumps(results, indent=4))
    #print(res)
    # convert 'results' to a string
    results_string = json.dumps(results)
    
    prompt = "Given the following context:\n" + results_string + "\nAnswer the following question:\n" + question_string + "provide a quote from the context to support your answer, and provide a summariziation of the relevant portions of the context."
    answer = ask_gpt(results, prompt)
    print(answer)

if __name__ == "__main__":
    main()
