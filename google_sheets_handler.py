
import json
import streamlit as st
from google.oauth2.service_account import Credentials
import gspread

class GoogleSheetHandler:
    def __init__(self, spreadsheet_name):
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive",
                 "https://www.googleapis.com/auth/drive.file"]

        credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        creds = Credentials.from_service_account_info(credentials_info, scopes=scope)
        self.client = gspread.authorize(creds)
        self.spreadsheet_name = spreadsheet_name  # Guardamos el nombre de la hoja, pero no accedemos a ninguna worksheet aún

    def read_data(self, sheet_name):
        sheet = self.client.open(self.spreadsheet_name).worksheet(sheet_name)
        data = sheet.get_all_records()
        return data

    def write_data(self, sheet_name, data):
        sheet = self.client.open(self.spreadsheet_name).worksheet(sheet_name)
        sheet.append_row(data)

    def clear_sheet(self, sheet_name):
        sheet = self.client.open(self.spreadsheet_name).worksheet(sheet_name)
        sheet.clear()
