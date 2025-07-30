import pandas as pd
import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

class GoogleSheetHandler:
    def __init__(self, spreadsheet_name):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        # Leer las credenciales desde los secrets
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open(spreadsheet_name)

    def read_sheet(self, sheet_name):
        worksheet = self.spreadsheet.worksheet(sheet_name)
        return pd.DataFrame(worksheet.get_all_records())

    def save_or_update_row(self, sheet_name, row_dict, key_field="Empresa"):
        worksheet = self.spreadsheet.worksheet(sheet_name)
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        columns = df.columns.tolist()

        if key_field not in row_dict:
            raise ValueError(f"'{key_field}' es obligatorio en row_dict")

        if df.empty or key_field not in df.columns:
            worksheet.append_row([row_dict.get(col, "") for col in columns])
            return

        match = df[df[key_field] == row_dict[key_field]]
        if not match.empty:
            index = match.index[0] + 2
            for col in columns:
                val = row_dict.get(col, "")
                worksheet.update_cell(index, columns.index(col) + 1, val)
        else:
            worksheet.append_row([row_dict.get(col, "") for col in columns])
