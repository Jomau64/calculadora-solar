import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import json

def test_google_sheets_connection():
    try:
        # Debug: Verificar que las credenciales existen
        if "GOOGLE_CREDENTIALS" not in st.secrets:
            st.error("❌ No se encontró 'GOOGLE_CREDENTIALS' en st.secrets")
            return False
        
        # Obtener credenciales
        credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Autenticación
        creds = Credentials.from_service_account_info(credentials_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Debug: Mostrar email de la cuenta de servicio
        service_account_email = creds.service_account_email
        st.info(f"🔑 Cuenta de servicio: {service_account_email}")
        
        # Nombre del archivo y hoja
        nombre_archivo = "Base de Datos Paneles Solares"
        nombre_hoja = "Paneles Solares"
        
        # Intentar abrir el archivo
        try:
            sheet = client.open(nombre_archivo)
        except gspread.SpreadsheetNotFound:
            st.error(f"❌ No se encontró el archivo: '{nombre_archivo}'")
            st.info("ℹ️ Asegúrate de:")
            st.info("1. Que el nombre sea exacto (copia-pega desde Google Sheets)")
            st.info(f"2. Que el archivo esté compartido con: {service_account_email}")
            return False
        
        # Intentar acceder a la hoja
        try:
            worksheet = sheet.worksheet(nombre_hoja)
        except gspread.WorksheetNotFound:
            st.error(f"❌ No se encontró la hoja: '{nombre_hoja}'")
            return False
        
        # Leer datos
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        st.success("✅ Conexión exitosa!")
        st.write(f"📊 Datos leídos: {len(df)} registros")
        st.dataframe(df.head(3))
        
        return True
    
    except Exception as e:
        st.error(f"❌ Error crítico: {str(e)}")
        return False

# Configuración de la página
st.set_page_config(page_title="Prueba de Conexión Google Sheets", layout="centered")
st.title("🔌 Prueba de Conexión a Google Sheets")

# Ejecutar prueba
if st.button("🧪 Probar Conexión"):
    with st.spinner("Conectando a Google Sheets..."):
        test_google_sheets_connection()