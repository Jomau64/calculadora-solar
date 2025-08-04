
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

class GoogleSheetHandler:
    def __init__(self, spreadsheet_name_or_id, by_id=False):
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials_info = st.secrets["GOOGLE_CREDENTIALS"]
        creds = Credentials.from_service_account_info(credentials_info, scopes=scope)
        self.client = gspread.authorize(creds)

        self.valid = True
        try:
            if by_id:
                self.sheet = self.client.open_by_key(spreadsheet_name_or_id)
            else:
                self.sheet = self.client.open(spreadsheet_name_or_id)
        except Exception as e:
            print(f"❌ No se pudo abrir el spreadsheet '{spreadsheet_name_or_id}': {e}")
            self.sheet = None
            self.valid = False

    def read_sheet(self, worksheet_name):
        if not self.valid or not self.sheet:
            return pd.DataFrame()
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            print(f"❌ Error al leer la hoja '{worksheet_name}': {e}")
            return pd.DataFrame()

class SheetsManager:
    def __init__(self):
        self.sheets = {}

    def get(self, spreadsheet_name, **kwargs):
        key = (spreadsheet_name, frozenset(kwargs.items()))
        if key not in self.sheets:
            self.sheets[key] = GoogleSheetHandler(spreadsheet_name, **kwargs)
        return self.sheets[key]
