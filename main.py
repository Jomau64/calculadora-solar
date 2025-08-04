import streamlit as st 
import pandas as pd
from componentes import ComponentesManager
from costos import CostosManager
from analisis_economico import AnalisisEconomico as AnalisisEconomicoManager
from google_sheets_handler import SheetsManager

st.set_page_config(
    page_title="Calculadora Solar",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_sheets_manager():
    return SheetsManager()

sheets_manager = get_sheets_manager()


class SolarAppGUI:
    def __init__(self):
        self.sheets = sheets_manager
        self.inicializar_datos()
        self.inicializar_managers()
        self.ensure_session_state()

    def inicializar_datos(self):
        with st.spinner("Cargando datos desde Google Sheets..."):
            if 'df_calculadora' not in st.session_state:
                st.session_state.df_calculadora = {}

                hojas = {
                    "Paneles": ("1cJwKj1fWp-ZVRaybO6PVTYacw1fjHrfLVBEHo7aMM7Y", "Paneles Solares", True),
                    "Inversores": ("1uiBBuLGl8hodfolqIq5mDo_X3Wxf0m6WMZgM0aSzDmQ", "Inversores", True),
                    "Baterías": ("1zzzzzzzzzzzzzzzzzzzzzzzzzzzzz", "Baterías", True),  # Reemplaza por el ID real de baterías
                    "Tarifas": ("1P4pxu687QhPrpKNNEAvi1eP17tYAk0KNOLAXA1lgCV8", "Pliego Tarifario", True),
                    "Estructura": ("1LZP8YNZZbqygkc7loqpEJrOslebEttE5xXfrwSRpGLc", "Materiales Estructura Solar", True),
                }

                for clave, valores in hojas.items():
                    try:
                        if len(valores) == 3:
                            archivo, hoja, by_id = valores
                        else:
                            archivo, hoja = valores
                            by_id = False

                        st.session_state.df_calculadora[clave] = self.sheets.get(archivo, by_id=by_id).read_sheet(hoja)
                    except Exception as e:
                        st.warning(f"⚠️ No se pudo cargar {clave}: Usando datos de ejemplo")
                        st.session_state.df_calculadora[clave] = pd.DataFrame({
                            "Modelo": ["Ejemplo 1", "Ejemplo 2"],
                            "Especificaciones": ["Valor 1", "Valor 2"]
                        })

    def inicializar_managers(self):
        from cliente import ClienteManager
        from equipamiento import EquipamientoManager
        from distribucion import DistribucionManager
        from estructura_solar import EstructuraSolar
        from distribucion_cadenas import DistribucionCadenas
        from generacion import Generacion

        if 'cliente_manager' not in st.session_state:
            st.session_state.cliente_manager = ClienteManager(st.session_state)

        if 'manager_equipamiento' not in st.session_state:
            st.session_state.manager_equipamiento = EquipamientoManager(st.session_state)

        if 'distribucion_manager' not in st.session_state:
            st.session_state.distribucion_manager = DistribucionManager(
                st.session_state.cliente_manager,
                st.session_state.manager_equipamiento,
                st.session_state
            )

        if 'estructura_solar' not in st.session_state:
            st.session_state.estructura_solar = EstructuraSolar(st.session_state)

        if 'distribucion_cadenas' not in st.session_state:
            st.session_state.distribucion_cadenas = DistribucionCadenas(st.session_state)

        if 'generacion' not in st.session_state:
            st.session_state.generacion = Generacion(st.session_state)

        if 'componentes_manager' not in st.session_state:
            st.session_state.componentes_manager = ComponentesManager(st.session_state)

        if 'costos_manager' not in st.session_state:
            st.session_state.costos_manager = CostosManager(st.session_state)

        if 'analisis_economico_manager' not in st.session_state:
            st.session_state.analisis_economico_manager = AnalisisEconomicoManager(st.session_state)

    def ensure_session_state(self):
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = "📝 Datos del Cliente"
        if 'distribucion_data' not in st.session_state:
            st.session_state.distribucion_data = {
                'panel_seleccionado': None,
                'paneles_por_array': {},
                'total_paneles': 0,
                'total_potencia': 0.0,
                'distribucion_actualizada': False,
                'arrays_config': [],
                'layout_data': {
                    'orientacion': 'Portrait',
                    'azimuth': '152°',
                    'pitch': '5°',
                    'ground_clearence': '',
                    'espacio_bordes': '1,00 Metros',
                    'filas_x_columna': '',
                    'columnas': '',
                    'total_filas_array': '',
                    'paneles_fila': '',
                    'paneles_columna': '',
                    'paneles_array': '',
                    'largo_fila': '',
                    'separacion_columnas': '',
                    'separacion_filas': ''
                }
            }

    def mostrar_botones_sidebar(self):
        if st.sidebar.button("💾 Guardar Proyecto", use_container_width=True):
            st.session_state.cliente_manager.guardar_proyecto_en_excel()

        if st.sidebar.button("🧹 Limpiar Campos", use_container_width=True):
            st.session_state.cliente_manager.limpiar_campos()

    def run(self):
        st.title("☀️ Calculadora Solar Integral")

        st.sidebar.markdown("<div class='sidebar-title'>Secciones</div>", unsafe_allow_html=True)
        seccion = st.sidebar.radio(
            "",
            ["📝 Datos del Cliente", "⚙️ Equipamientos", "☀️ Distribución Solar",
             "📐 Estructura Solar", "🔗 Distribución de Cadenas", "⚡ Generación",
             "📦 Componentes", "💰 Costos", "📊 Análisis Económico"],
            key="menu_seccion"
        )

        self.mostrar_botones_sidebar()

        if seccion == "📝 Datos del Cliente":
            st.session_state.cliente_manager.mostrar_pestana()
        elif seccion == "⚙️ Equipamientos":
            st.session_state.manager_equipamiento.mostrar_pestana()
        elif seccion == "☀️ Distribución Solar":
            st.session_state.distribucion_manager.mostrar_pestana()
        elif seccion == "📐 Estructura Solar":
            st.session_state.estructura_solar.mostrar_panel()
        elif seccion == "🔗 Distribución de Cadenas":
            st.session_state.distribucion_cadenas.mostrar_pestana()
        elif seccion == "⚡ Generación":
            st.session_state.generacion.mostrar_pestana()
        elif seccion == "📦 Componentes":
            st.session_state.componentes_manager.mostrar_pestana()
        elif seccion == "💰 Costos":
            st.session_state.costos_manager.mostrar_pestana()
        elif seccion == "📊 Análisis Económico":
            st.session_state.analisis_economico_manager.mostrar_pestana()


if __name__ == "__main__":
    app = SolarAppGUI()
    app.run()
