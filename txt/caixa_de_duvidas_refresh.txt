from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def create_sheets_client():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'C:\\Users\\LiveBot\\Desktop\\LIVINHA\\chatbotliveslack-2363fb0deb69.json'

    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=credentials)
    return service.spreadsheets()

def insert_data_into_sheet(values):
    # print(f"Chamando insert_data_into_sheet com valores: {values}")  # Adicione esta linha
    sheets_client = create_sheets_client()
    body = {
        'values': values
    }
    range_name = 'Página1!A1:A'
    # print(f"Tentando inserir na planilha: {values}")  # Adicione esta linha
    result = sheets_client.values().append(
        spreadsheetId='1TJjbWRcsyHV_f56MoVK4bkLLd7NMc4PQ917SLBAzhoU', range=range_name,
        valueInputOption='USER_ENTERED', body=body, insertDataOption='INSERT_ROWS').execute()
    #print(f"Resultado da inserção: {result}")  # Adicione esta linha
    # print(f"{result.get('updates').get('updatedCells')} cells appended.")
    
if __name__ == "__main__":
    # Substitua 'Texto de exemplo' pelo texto que você quer inserir na planilha
    test_values = [["Texto de exemplo"]]
    # print("Testando a inserção direta na planilha do Google Sheets")
    insert_data_into_sheet(test_values)
