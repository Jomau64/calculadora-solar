import streamlit as st
import gspread
import pandas as pd
import json
from google.oauth2.service_account import Credentials

class GoogleSheetHandler:
    def __init__(self, spreadsheet_name_or_id, by_id=False):
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        # 🟢 Usa st.secrets en lugar de credentials.json
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

        self.client = gspread.authorize(creds)
        self.valid = True

        try:
            if by_id:
                self.sheet = self.client.open_by_key(spreadsheet_name_or_id)
            else:
                self.sheet = self.client.open(spreadsheet_name_or_id)
        except Exception:
            self.sheet = None
            self.valid = False

    def read_sheet(self, worksheet_name):
        if not self.valid or not self.sheet:
            return pd.DataFrame()

        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            data = worksheet.get_all_records()
            return pd.DataFrame(data) if data else pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def save_or_update_row(self, worksheet_name, new_data: dict, key_field="Empresa"):
        print(f"💾 save_or_update_row ejecutado para hoja '{worksheet_name}' con clave '{new_data.get(key_field)}'")

        if not self.valid or not self.sheet:
            return "error_sin_conexion"

        try:
            worksheet = self.sheet.worksheet(worksheet_name)

            current_headers = worksheet.row_values(1)
            all_keys = list(new_data.keys())

            new_columns = [k for k in all_keys if k not in current_headers]
            if new_columns:
                current_headers += new_columns
                worksheet.update('A1', [current_headers])

            all_values = worksheet.get_all_values()
            rows = all_values[1:]
            df = pd.DataFrame(rows, columns=current_headers) if rows else pd.DataFrame(columns=current_headers)
            df.fillna("", inplace=True)

            print("📋 Datos a guardar:", new_data)

            ordered_values = [str(new_data.get(col, "")) for col in current_headers]

            if key_field in df.columns and new_data.get(key_field, "") in df[key_field].values:
                idx = df[df[key_field] == new_data[key_field]].index[0] + 2
                end_col = colnum_to_excel_col(len(current_headers))
                worksheet.update(f"A{idx}:{end_col}{idx}", [ordered_values])
                print("✅ Fila actualizada correctamente")
                return "updated"
            else:
                worksheet.append_row(ordered_values)
                print("✅ Fila insertada correctamente")
                return "inserted"

        except Exception as e:
            print("❌ ERROR en save_or_update_row:", str(e))
            import traceback
            traceback.print_exc()
            return f"error: {str(e)}"

def colnum_to_excel_col(n):
    col = ''
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        col = chr(65 + remainder) + col
    return col

class SheetsManager:
    def __init__(self):
        self.sheets = {}

    def get(self, spreadsheet_name, **kwargs):
        key = (spreadsheet_name, frozenset(kwargs.items()))
        if key not in self.sheets:
            self.sheets[key] = GoogleSheetHandler(spreadsheet_name, **kwargs)
        return self.sheets[key]
