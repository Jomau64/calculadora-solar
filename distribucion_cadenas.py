import streamlit as st
import pandas as pd
from math import ceil
from equipamiento import limpiar_float

class DistribucionCadenas:
    def __init__(self, session_state):
        self.session_state = session_state

    def mostrar_pestana(self):
        st.header("🔗 Distribución de Cadenas")

        panel_sel = self.session_state.equipamiento_seleccionado.get("Paneles Solares")
        inversor_sel = self.session_state.equipamiento_seleccionado.get("Inversores")
        distribucion_data = self.session_state.get('distribucion_data', {})

        df_paneles = self.session_state.manager_equipamiento.df_equipamientos.get("Paneles Solares", None)
        df_inversores = self.session_state.manager_equipamiento.df_equipamientos.get("Inversores", None)

        if not panel_sel or not inversor_sel:
            st.warning("Debe seleccionar un **Panel Solar** y un **Inversor** en la pestaña Equipamientos.")
            return

        st.markdown("""<style>
        .titulo-cuadro {
            background-color: #0d3b0d;
            color: white;
            padding: 10px 16px;
            font-weight: bold;
            font-size: 18px;
            border-radius: 6px;
            margin-bottom: 6px;
        }
        .stTable th {
            background-color: #e8f5e9 !important;
            color: #000;
            font-size: 16px !important;
        }
        .stTable td {
            font-size: 15px !important;
        }
        </style>""", unsafe_allow_html=True)

        df_inv = df_inversores[df_inversores['nombre_display'] == inversor_sel]
        inv = df_inv.iloc[0] if not df_inv.empty else {}

        df_pan = df_paneles[df_paneles['nombre_display'] == panel_sel]
        pan = df_pan.iloc[0] if not df_pan.empty else {}

        try:
            voc_ajustado = round(float(pan.get("VOC", 0)) * 1.028, 2)
        except:
            voc_ajustado = 0

        try:
            max_pv_voltage = limpiar_float(inv.get("Max PV Input Voltage", 0))
            max_panels_per_string = int(max_pv_voltage // voc_ajustado)
        except:
            max_panels_per_string = 1

        try:
            total_paneles = int(distribucion_data.get("total_paneles", 0))
            noct = limpiar_float(pan.get("NOCT", 0))
            capacidad_inversor = limpiar_float(inv.get("Capacidad", 0))

            val1 = ceil((total_paneles * noct) / 1000 / capacidad_inversor)
            val2 = ceil(total_paneles / (max_panels_per_string * int(limpiar_float(inv.get("Strings", 1)))))
            cantidad_inversores = max(val1, val2)
        except:
            cantidad_inversores = 1

        self.session_state["datos_distribucion_cadenas"] = {
            "cantidad_inversores": cantidad_inversores
        }

        # Cuadro Inversor
        st.markdown("<div class='titulo-cuadro'>Inversor</div>", unsafe_allow_html=True)
        st.markdown(f"**{inversor_sel}**")
        st.table({
            "Parámetro": [
                "Cantidad de inversores (calculado)",
                "Rated PV Acess Voltage DC",
                "MPPT",
                "Strings",
                "Max Paneles por string"
            ],
            "Valor": [
                cantidad_inversores,
                str(int(limpiar_float(inv.get("Max PV Input Voltage", 0)))),
                str(int(limpiar_float(inv.get("MPPT", 0)))),
                str(int(limpiar_float(inv.get("Strings", 0)))),
                max_panels_per_string
            ]
        })

        # Cuadro Panel
        st.markdown("<div class='titulo-cuadro'>Panel Solar</div>", unsafe_allow_html=True)
        st.markdown(f"**{panel_sel}**")
        st.table({
            "Parámetro": ["Capacidad", "VOC (ajustado)"],
            "Valor": [
                str(int(limpiar_float(pan.get("Capacidad", 0)))) + " kW",
                str(voc_ajustado) + " VDC"
            ]
        })

        # Cuadro MPPT
        try:
            mppt = int(limpiar_float(inv.get("MPPT", 0)))
            strings = int(limpiar_float(inv.get("Strings", 0)))
            cadenas_por_mppt = strings // mppt if mppt else 0
            total_cadenas = mppt * cadenas_por_mppt
            paneles_por_cadena = max_panels_per_string
        except:
            mppt = cadenas_por_mppt = total_cadenas = paneles_por_cadena = "N/A"

        st.markdown("<div class='titulo-cuadro'>MPPT</div>", unsafe_allow_html=True)
        st.table({
            "Parámetro": [
                "Cantidad MPPT",
                "Cadenas por MPPT",
                "Total de Cadenas",
                "Paneles por Cadena"
            ],
            "Valor": [
                mppt,
                cadenas_por_mppt,
                total_cadenas,
                paneles_por_cadena
            ]
        })

        # Cuadro Cadenas
        try:
            voc_total = int(total_paneles * voc_ajustado)
            rated_pv_access = limpiar_float(inv.get("Max PV Input Voltage", 0))
            total_cadenas_calc = ceil(voc_total / rated_pv_access)
        except:
            voc_total = total_cadenas_calc = "N/A"

        st.markdown("<div class='titulo-cuadro'>Cadenas</div>", unsafe_allow_html=True)
        st.table({
            "Parámetro": [
                "Paneles Solares",
                "VOC",
                "Cadenas"
            ],
            "Valor": [
                f"{total_paneles} Paneles",
                f"{voc_total} VDC",
                total_cadenas_calc
            ]
        })

        # Cuadro Distribución
        try:
            panel_id = 1
            filas_distribucion = []

            for inv_num in range(1, cantidad_inversores + 1):
                for mppt in [1, 2]:
                    fila = {
                        "Inversor": f"{inversor_sel} ({inv_num})",
                        "MPPT": mppt,
                        "Input 1": "", "Input 2": "", "Input 3": "", "Input 4": "", "Input 5": ""
                    }
                    for input_num in range(1, 6):
                        if panel_id > total_paneles:
                            break
                        if (mppt == 1 and input_num <= 4) or (mppt == 2 and input_num <= 2):
                            inicio = panel_id
                            fin = min(panel_id + paneles_por_cadena - 1, total_paneles)
                            fila[f"Input {input_num}"] = f"P{inicio} - P{fin}"
                            panel_id = fin + 1
                    filas_distribucion.append(fila)

            df_distribucion = pd.DataFrame(filas_distribucion)
            df_distribucion = df_distribucion[["Inversor", "MPPT", "Input 1", "Input 2", "Input 3", "Input 4", "Input 5"]]

            st.markdown("<div class='titulo-cuadro'>Distribución</div>", unsafe_allow_html=True)
            st.markdown("""<style>
            .dist-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            .dist-table th {
                background-color: #0b6623;
                color: white;
                padding: 10px;
                text-align: center;
                font-weight: bold;
            }
            .dist-table td {
                border: 1px solid #ddd;
                padding: 8px 12px;
                text-align: center;
            }
            .dist-table tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            </style>""", unsafe_allow_html=True)

            html_table = df_distribucion.to_html(index=False, classes="dist-table", justify="center")
            st.write(html_table, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error en distribución: {e}")