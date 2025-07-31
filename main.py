
import streamlit as st
import os
from pathlib import Path
import pandas as pd

from componentes import ComponentesManager
from costos import CostosManager
from analisis_economico import AnalisisEconomico as AnalisisEconomicoManager

st.set_page_config(
    page_title="Calculadora Solar",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp { max-width: 1600px; padding: 1rem; }
.stTextInput input, .stSelectbox select {
    padding: 0.3rem 0.5rem !important; font-size: 0.9rem !important;
}
.stDataFrame { font-size: 0.8rem; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { margin-top: 0.5rem !important; }

.sidebar-title {
    font-weight: bold;
    font-size: 20px;
    margin-bottom: 1rem;
}

.sidebar-radio label {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)


def cargar_excel_local(nombre_archivo):
    ruta_base = Path(__file__).parent.resolve()
    ruta_archivo = ruta_base / nombre_archivo

    if not ruta_archivo.exists():
        st.error(f"❌ No se encontró el archivo local '{nombre_archivo}' en:\n{ruta_archivo}")
        st.stop()

    try:
        # Cargar todas las hojas
        excel = pd.read_excel(ruta_archivo, sheet_name=None)
        return excel
    except Exception as e:
        st.error(f"Error al cargar el archivo '{nombre_archivo}': {str(e)}")
        st.stop()


class SolarAppGUI:
    def __init__(self):
        self.inicializar_datos()
        self.inicializar_managers()
        self.ensure_session_state()

    def inicializar_datos(self):
        with st.spinner("Cargando archivos locales..."):
            if 'df_calculadora' not in st.session_state:
                calculadora = cargar_excel_local("Calculadora Solar.xlsx")
                st.session_state.df_calculadora = {
                    "Paneles": calculadora.get("Paneles Solares", ""),
                    "Inversores": calculadora.get("Inversores", ""),
                   "Baterías": calculadora.get("Baterías", ""),
                }

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
        # Botones funcionales de Streamlit
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
