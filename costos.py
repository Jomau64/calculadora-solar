import streamlit as st
import pandas as pd
from google_sheets_handler import GoogleSheetHandler
from equipamiento import limpiar_float

class CostosManager:
    def __init__(self, session_state):
        self.session_state = session_state

    def mostrar_pestana(self):
        st.header("💰 Costos del Proyecto")

        # Factores
        factor1 = 1.22
        factor2 = 1.57
        margen = 0.20  # 20%

        # Encabezado de factores
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Factor 1**")
            st.write(factor1)
        with col2:
            st.markdown("**Factor 2**")
            st.write(factor2)
        with col3:
            st.markdown("**Margen**")
            st.write("20%")

        st.divider()

        # Datos seleccionados
        componentes = self.session_state.get("componentes_principales", {})
        panel_sel = self.session_state.equipamiento_seleccionado.get("Paneles Solares", "")
        inversor_sel = self.session_state.equipamiento_seleccionado.get("Inversores", "")
        cantidad_paneles = componentes.get("Paneles Solares", 0)
        cantidad_inversores = componentes.get("Inversores", 0)
        cantidad_baterias = componentes.get("Baterías de almacenamiento", 0)
        cantidad_convertidor = componentes.get("Convertidor de alto voltaje DC", 0)
        cantidad_mppt = componentes.get("Controladores de carga MPPT", 0)

        fob_ch_panel = 0.0
        fob_ch_inversor = 0.0

        # Paneles Solares
        try:
            sheet_paneles = GoogleSheetHandler("Base de Datos Paneles Solares")
            df_paneles = sheet_paneles.read_sheet("Paneles Solares")
            df_paneles["Modelo_clean"] = df_paneles["Modelo"].astype(str).str.strip().str.lower()
            panel_sel_clean = panel_sel.strip().lower()
            match = df_paneles[df_paneles["Modelo_clean"].str.contains(panel_sel_clean.split()[-1], na=False)]
            if not match.empty:
                fob_ch_panel = limpiar_float(match.iloc[0]["FOB CH"])
            else:
                st.warning(f"No se encontró un modelo de panel compatible con: '{panel_sel}'")
        except Exception as e:
            st.error(f"Error al leer FOB CH del panel: {e}")

        # Inversores
        try:
            sheet_inversores = GoogleSheetHandler("Base de Datos Inversores")
            df_inversores = sheet_inversores.read_sheet("Inversores")
            df_inversores["Modelo_clean"] = df_inversores["Modelo"].astype(str).str.strip().str.lower()
            inversor_sel_clean = inversor_sel.strip().lower()
            match = df_inversores[df_inversores["Modelo_clean"].str.contains(inversor_sel_clean.split()[-1], na=False)]
            if not match.empty:
                fob_ch_inversor = limpiar_float(match.iloc[0]["FOB CH"])
            else:
                st.warning(f"No se encontró un modelo de inversor compatible con: '{inversor_sel}'")
        except Exception as e:
            st.error(f"Error al leer FOB CH del inversor: {e}")

        # Estructura Solar - FOB CH desde Total Materiales
        try:
            estructura_df = self.session_state.get("estructura_total_materiales", pd.DataFrame())
            if not estructura_df.empty:
                total_col = next((col for col in estructura_df.columns if col.lower() == "total"), None)
                if total_col is not None:
                    estructura_df[total_col] = pd.to_numeric(estructura_df[total_col], errors='coerce')
                    fob_ch_estructura = estructura_df[total_col].sum()
                else:
                    st.warning("No se encontró una columna de totales en estructura_total_materiales.")
                    fob_ch_estructura = 0.0
            else:
                st.warning("No hay datos en estructura_total_materiales.")
                fob_ch_estructura = 0.0
        except Exception as e:
            st.error(f"Error al calcular FOB CH de Estructura Solar: {e}")
            fob_ch_estructura = 0.0

        # Cálculos
        fob_uio_panel = fob_ch_panel * factor1
        fob_uio_inversor = fob_ch_inversor * factor1
        fob_uio_estructura = fob_ch_estructura * factor2

        pvp_panel = fob_uio_panel / (1 - margen) if fob_uio_panel else 0.0
        pvp_inversor = fob_uio_inversor / (1 - margen) if fob_uio_inversor else 0.0
        pvp_estructura = fob_uio_estructura / (1 - margen) if fob_uio_estructura else 0.0

        datos = [
            ["Paneles Solares", cantidad_paneles, fob_ch_panel, fob_uio_panel, pvp_panel],
            ["Inversores", cantidad_inversores, fob_ch_inversor, fob_uio_inversor, pvp_inversor],
            ["Baterías de almacenamiento", cantidad_baterias, 0.00, 0.00, 0.00],
            ["Convertidor de alto voltaje DC", cantidad_convertidor, 0.00, 0.00, 0.00],
            ["Controladores de carga MPPT", cantidad_mppt, 0.00, 0.00, 0.00],
            ["Estructura Solar", 1, fob_ch_estructura, fob_uio_estructura, pvp_estructura],
            ["Material Eléctrico", 1, 0.00, 0.00, 0.00],
        ]

        df_temp = pd.DataFrame(datos, columns=["Detalle", "Cantidad", "FOB CH", "FOB UIO", "PVP"])
        df_temp["Total UIO"] = df_temp["Cantidad"] * df_temp["FOB UIO"]

        componentes_base = ["Paneles Solares", "Inversores", "Baterías de almacenamiento", "Controladores de carga MPPT", "Estructura Solar"]
        suma_total_uio_base = df_temp[df_temp["Detalle"].isin(componentes_base)]["Total UIO"].sum()

        fob_uio_obra_civil = suma_total_uio_base * 0.03
        fob_uio_instalacion = suma_total_uio_base * 0.05
        fob_uio_miscelaneus = suma_total_uio_base * 0.02

        datos += [
            ["Obra Civil", 1, 0.00, fob_uio_obra_civil, fob_uio_obra_civil / (1 - margen)],
            ["Instalación", 1, 0.00, fob_uio_instalacion, fob_uio_instalacion / (1 - margen)],
            ["Miscelaneus", 1, 0.00, fob_uio_miscelaneus, fob_uio_miscelaneus / (1 - margen)],
        ]

        df = pd.DataFrame(datos, columns=["Detalle", "Cantidad", "FOB CH", "FOB UIO", "PVP"])
        df["Total UIO"] = df["Cantidad"] * df["FOB UIO"]
        df["Total PVP"] = df["Cantidad"] * df["PVP"]
        df["Ganancia"] = df["Total PVP"] - df["Total UIO"]

        self.session_state["costos_data"] = df

        inversion_total = df["Total UIO"].sum()
        pvp_total = df["Total PVP"].sum()
        ganancia_total = df["Ganancia"].sum()

        col_izq, col_der = st.columns([3, 1.2])

        with col_izq:
            st.markdown("### 📋 Detalle de Costos")
            st.dataframe(
                df.style.format({
                    "FOB CH": lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x,
                    "FOB UIO": lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x,
                    "PVP": lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x,
                    "Total UIO": lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x,
                    "Total PVP": lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x,
                    "Ganancia": lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x,
                }),
                use_container_width=True
            )

            st.markdown(f"""
            <div style='font-size:16px; margin-top:10px;'>
                <strong>Inversión Total:</strong> ${inversion_total:.2f}<br>
                <strong>Total PVP:</strong> ${pvp_total:.2f}
            </div>
            """, unsafe_allow_html=True)

        with col_der:
            st.markdown("### 💹 Ganancia")
            html_ganancia = "<table style='width:100%; font-size:16px;'>"
            for _, row in df.iterrows():
                html_ganancia += f"<tr><td>{row['Detalle']}</td><td style='text-align:right;'>${row['Ganancia']:.2f}</td></tr>"
            html_ganancia += "</table>"
            st.markdown(html_ganancia, unsafe_allow_html=True)
            st.markdown(f"""
            <div style='margin-top:15px; font-size:16px; color:green; font-weight:bold;'>
                Ganancia Total: ${ganancia_total:.2f}
            </div>
            """, unsafe_allow_html=True)
