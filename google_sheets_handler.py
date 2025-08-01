import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

class GoogleSheetHandler:
    def __init__(self, spreadsheet_name, sheet_name=None):
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open(spreadsheet_name)
        self.worksheet = self.spreadsheet.worksheet(sheet_name) if sheet_name else self.spreadsheet.sheet1

    def get_all_records(self):
        return self.worksheet.get_all_records()

    def get_all_values(self):
        return self.worksheet.get_all_values()

    def update_cell(self, row, col, value):
        self.worksheet.update_cell(row, col, value)

    def append_row(self, row_values):
        self.worksheet.append_row(row_values)

    def clear(self):
        self.worksheet.clear()
