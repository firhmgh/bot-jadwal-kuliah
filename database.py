import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    creds_json = os.getenv("GOOGLE_CREDS")
    sheet_id = os.getenv("SHEET_ID")
    
    if not creds_json or not sheet_id:
        raise Exception("GOOGLE_CREDS atau SHEET_ID belum disetting di Environment Variables!")

    creds_dict = json.loads(creds_json)
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    return client.open_by_key(sheet_id)