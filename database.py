import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # Mengambil credential dari .env
    creds_json = os.getenv("GOOGLE_CREDS")
    sheet_id = os.getenv("SHEET_ID")
    
    # Konversi string JSON ke Dictionary Python
    creds_dict = json.loads(creds_json)
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    return client.open_by_key(sheet_id)