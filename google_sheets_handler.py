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

        try:
            credentials_info = st.secrets["GOOGLE_CREDENTIALS"]
            creds = Credentials.from_service_account_info(credentials_info, scopes=scope)
            self.client = gspread.authorize(creds)
        except Exception as e:
            st.error(f"❌ Error al autenticar con Google API: {e}")
            self.client = None
            self.valid = False
            return

        self.valid = True
        try:
            if by_id:
                self.sheet = self.client.open_by_key(spreadsheet_name_or_id)
            else:
                self.sheet = self.client.open(spreadsheet_name_or_id)
        except Exception as e:
            st.error(f"❌ No se pudo abrir el spreadsheet: {e}")
            self.sheet = None
            self.valid = False

    def read_sheet(self, worksheet_name):
        if not self.valid or not self.sheet:
            return pd.DataFrame()
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            data = worksheet.get_all_records()
            return pd.DataFrame(data) if data else pd.DataFrame()
        except Exception as e:
            st.error(f"❌ Error al leer la hoja '{worksheet_name}': {e}")
            return pd.DataFrame()

    def save_or_update_row(self, worksheet_name, new_data: dict, key_field="Empresa"):
        if not self.valid or not self.sheet:
            return "error_sin_conexion"
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            current_headers = worksheet.row_values(1)
            new_keys = list(new_data.keys())

            # Agregar nuevas columnas si no existen
            missing_cols = [k for k in new_keys if k not in current_headers]
            if missing_cols:
                current_headers += missing_cols
                worksheet.update('A1', [current_headers])

            # Leer datos actuales
            all_values = worksheet.get_all_values()
            rows = all_values[1:]
            df = pd.DataFrame(rows, columns=current_headers) if rows else pd.DataFrame(columns=current_headers)
            df.fillna("", inplace=True)

            ordered = [str(new_data.get(col, "")) for col in current_headers]

            if key_field in df.columns and new_data.get(key_field, "") in df[key_field].values:
                idx = df[df[key_field] == new_data[key_field]].index[0] + 2
                end_col = colnum_to_excel_col(len(current_headers))
                worksheet.update(f"A{idx}:{end_col}{idx}", [ordered])
                return "updated"
            else:
                worksheet.append_row(ordered)
                return "inserted"

        except Exception as e:
            st.error(f"❌ Error al guardar en hoja '{worksheet_name}': {e}")
            return f"error: {e}"

def colnum_to_excel_col(n):
    col = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        col = chr(65 + r) + col
    return col

class SheetsManager:
    def __init__(self):
        self.sheets = {}

    def get(self, spreadsheet_name, **kwargs):
        key = (spreadsheet_name, frozenset(kwargs.items()))
        if key not in self.sheets:
            self.sheets[key] = GoogleSheetHandler(spreadsheet_name, **kwargs)
        return self.sheets[key]
