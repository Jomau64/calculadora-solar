import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import json

# Obtener credenciales desde secrets
try:
    credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(credentials_info, scopes=scope)
    client = gspread.authorize(creds)

    # Nombre exacto del archivo y hoja
    nombre_archivo = "Base de Datos Paneles Solares"
    nombre_hoja = "Paneles Solares"

    # Cargar hoja
    sheet = client.open(nombre_archivo)
    worksheet = sheet.worksheet(nombre_hoja)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    st.success("✅ Conexión exitosa a Google Sheets")
    st.write(df)

except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
