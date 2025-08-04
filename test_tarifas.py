
import streamlit as st
from google_sheets_handler import GoogleSheetHandler

st.set_page_config(page_title="🔍 Test Tarifa ARCONEL", layout="centered")

st.title("🔍 Test de conexión a hoja de Tarifas")

# ID de la hoja de Google Sheets
sheet_id = "1P4pxu687QhPrpKNNEAvi1eP17tYAk0KNOLAXA1lgCV8"
sheet_name = "Pliego Tarifario"

# Crear instancia del handler
handler = GoogleSheetHandler(sheet_id, by_id=True)

# Leer hoja
df = handler.read_sheet(sheet_name)

# Mostrar resultados
if df.empty:
    st.error("❌ No se pudo leer datos de la hoja 'Pliego Tarifario'.")
    st.info("Verifica que el archivo esté compartido con la cuenta de servicio y tenga encabezados.")
else:
    st.success(f"✅ Se leyeron {df.shape[0]} filas de la hoja.")
    st.dataframe(df)
