import streamlit as st
import pandas as pd
from math import ceil

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

        # Estilo visual mejorado
        st.markdown("""
        <style>
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
        </style>
        """, unsafe_allow_html=True)

        df_inv = df_inversores[df_inversores['nombre_display'] == inversor_sel]
        inv = df_inv.iloc[0] if not df_inv.empty else {}

        df_pan = df_paneles[df_paneles['nombre_display'] == panel_sel]
        pan = df_pan.iloc[0] if not df_pan.empty else {}

        # VOC Ajustado
        try:
            voc_original = float(pan.get("VOC", 0))
            voc_ajustado = round(voc_original * 1.028, 2)
        except:
            voc_ajustado = "N/A"

        # Max Paneles por string
        try:
            max_pv_voltage = float(inv.get("Max PV Input Voltage", 0))
            max_panels_per_string = int(max_pv_voltage // voc_ajustado)
        except:
            max_panels_per_string = "N/A"

        # Cálculo: Cantidad de inversores (calculado)
        try:
            total_paneles = int(distribucion_data.get("total_paneles", 0))
            noct = float(pan.get("NOCT", 0))
            potencia_total_kw = (total_paneles * noct) / 1000
            capacidad_inversor = float(inv.get("Capacidad", 0))

            val1 = ceil(potencia_total_kw / capacidad_inversor)
            val2 = ceil(total_paneles / (max_panels_per_string * int(float(inv.get("Strings", 1)))))
            cantidad_inversores = max(val1, val2)
        except:
            cantidad_inversores = "N/A"


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
                str(int(float(inv.get("Max PV Input Voltage", 0)))),
                str(int(float(inv.get("MPPT", 0)))),
                str(int(float(inv.get("Strings", 0)))),
                max_panels_per_string
            ]
        })

        # Cuadro Panel Solar
        st.markdown("<div class='titulo-cuadro'>Panel Solar</div>", unsafe_allow_html=True)
        st.markdown(f"**{panel_sel}**")
        st.table({
            "Parámetro": ["Capacidad", "VOC (ajustado)"],
            "Valor": [
                str(int(float(pan.get("Capacidad", 0)))) + " kW",
                str(voc_ajustado) + " VDC"
            ]
        })

        # Cuadro MPPT
        try:
            mppt = int(float(inv.get("MPPT", 0)))
            strings = int(float(inv.get("Strings", 0)))
            cadenas_por_mppt = int(strings // mppt) if mppt else "N/A"
            total_cadenas = mppt * cadenas_por_mppt if isinstance(cadenas_por_mppt, int) else "N/A"
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
            rated_pv_access = float(inv.get("Max PV Input Voltage", 0))
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
            cantidad_inversores = int(cantidad_inversores)
            nombre_inversor = inversor_sel
            paneles_por_cadena = max_panels_per_string
            total_paneles = int(total_paneles)
    
            # Crear estructura para la distribución (como en tu ejemplo)
            filas_distribucion = []
            panel_id = 1
    
            for inv_num in range(1, cantidad_inversores + 1):
                 for mppt in [1, 2]:  # Asumiendo 2 MPPT por inversor (como en tu ejemplo)
                    # Crear fila para este MPPT
                    fila = {
                        "Inversor": f"{nombre_inversor} ({inv_num})",
                        "MPPT": mppt,
                        "Input 1": "",
                        "Input 2": "",
                        "Input 3": "",
                        "Input 4": "",
                        "Input 5": ""
                    }
            
                    # Llenar los inputs para este MPPT (máximo 2 strings llenos por MPPT como en tu ejemplo)
                    for input_num in range(1, 6):  # Inputs 1 a 5
                        if panel_id > total_paneles:
                           break
                    
                        if mppt == 1 and input_num <= 4:  # MPPT 1 tiene hasta 4 inputs llenos
                            inicio = panel_id
                            fin = min(panel_id + paneles_por_cadena - 1, total_paneles)
                            fila[f"Input {input_num}"] = f"P{inicio} - P{fin}"
                            panel_id = fin + 1
                        elif mppt == 2 and input_num <= 2:  # MPPT 2 tiene hasta 2 inputs llenos
                            inicio = panel_id
                            fin = min(panel_id + paneles_por_cadena - 1, total_paneles)
                            fila[f"Input {input_num}"] = f"P{inicio} - P{fin}"
                            panel_id = fin + 1
            
                    filas_distribucion.append(fila)
    
            # Mostrar la tabla de distribución (EXACTAMENTE como en tu ejemplo)
            st.markdown("<div class='titulo-cuadro'>Distribución</div>", unsafe_allow_html=True)
    
            # Estilo específico para esta tabla
            st.markdown("""
            <style>
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
            </style>
            """, unsafe_allow_html=True)
    
            # Crear y mostrar DataFrame
            df_distribucion = pd.DataFrame(filas_distribucion)
    
            # Reordenar columnas exactamente como en tu ejemplo
            column_order = ["Inversor", "MPPT", "Input 1", "Input 2", "Input 3", "Input 4", "Input 5"]
            df_distribucion = df_distribucion[column_order]
    
            # Convertir a HTML para mayor control visual
            html_table = df_distribucion.to_html(
                index=False, 
                classes="dist-table",
                justify="center"
            )
    
            # Ajustes finales al HTML
            html_table = html_table.replace(' style="text-align: center;"', '')  # Eliminar alineación por defecto
            st.write(html_table, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error en distribución: {e}")