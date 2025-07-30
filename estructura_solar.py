import streamlit as st
import pandas as pd  # <-- ESTA LÍNEA FALTABA
import math
from typing import Dict, List
from copy import deepcopy
from streamlit.components.v1 import html

class EstructuraSolar:
    def __init__(self, session_state):
        self.session_state = session_state

    def mostrar_panel(self):
        st.header("📐 Estructura Solar")
        panel_sel = self.session_state.equipamiento_seleccionado.get('Paneles Solares', "").strip()
        if not panel_sel:
            st.warning("No se ha seleccionado ningún panel solar en el proyecto")
            return

        panel_data = self.obtener_datos_panel()
        self.mostrar_info_panel(panel_data)
        self.mostrar_estructura_basica()
        self.mostrar_materiales_por_array()
        self.mostrar_total_materiales()

    def obtener_datos_panel(self) -> Dict:
        panel_nombre = self.session_state.equipamiento_seleccionado['Paneles Solares']
        df_paneles = self.session_state.manager_equipamiento.df_equipamientos['Paneles Solares']

        if df_paneles.empty:
            raise ValueError("No hay datos de paneles solares disponibles")

        panel_data = df_paneles[df_paneles['nombre_display'] == panel_nombre].iloc[0].to_dict()

        medidas = {
            'Alto': float(panel_data.get('Alto', 0)),
            'Ancho': float(panel_data.get('Ancho', 0)),
            'Espesor': float(panel_data.get('Espesor', 0)),
            'Metros²': float(panel_data.get('Metros²', 0))
        }

        if any(value <= 0 for value in medidas.values()):
            raise ValueError("Medidas del panel solar inválidas")

        return {**panel_data, **medidas}

    def mostrar_info_panel(self, panel_data: Dict):
        with st.container(border=True):
            st.subheader("Panel Solar")

            html_content = f"""
            <table class="panel-table">
                <tr><th>Dimensiones</th><th>Especificación</th><th>Medidas</th></tr>
                <tr><td>Largo</td><td>Medida Portrait (Y)</td><td>{panel_data['Alto']:.3f} M</td></tr>
                <tr><td>Ancho</td><td>Medida Landscape (X)</td><td>{panel_data['Ancho']:.3f} M</td></tr>
                <tr><td>Espesor</td><td>Grosor del panel</td><td>{panel_data['Espesor']:.3f} M</td></tr>
                <tr><td>Área</td><td>(Largo × Ancho)</td><td>{panel_data['Metros²']:.3f} M²</td></tr>
                <tr><td>Watts</td><td>Capacidad Nominal</td><td>{int(float(panel_data.get('Capacidad', 0)))} W</td></tr>
            </table>
            <style>
            .panel-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 1rem 0;
                font-family: Arial, sans-serif;
            }}
            .panel-table th {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 0.75rem;
                text-align: left;
            }}
            .panel-table td {{
                border: 1px solid #dee2e6;
                padding: 0.75rem;
            }}
            .panel-table tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            </style>
            """
            st.markdown(html_content, unsafe_allow_html=True)

    def mostrar_estructura_basica(self):
        with st.container(border=True):
            st.subheader("Componentes Estructurales Básicos")

            html_content = """
            <table class="estructura-table">
                <tr><th>Componente</th><th>Dimensión</th><th>Descripción</th></tr>
                <tr><td>End Clamp</td><td>0.030 M</td><td>Sujeción lateral</td></tr>
                <tr><td>Mid Clamp</td><td>0.021 M</td><td>Sujeción intermedia</td></tr>
                <tr><td>L Foot</td><td>0.000 M</td><td>Soporte de montaje</td></tr>
            </table>
            <style>
            .estructura-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 1rem 0;
                font-family: Arial, sans-serif;
            }}
            .estructura-table th {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 0.75rem;
                text-align: left;
            }}
            .estructura-table td {{
                border: 1px solid #dee2e6;
                padding: 0.75rem;
            }}
            .estructura-table tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            </style>
            """
            st.markdown(html_content, unsafe_allow_html=True)

    def obtener_configuracion_distribucion_solar(self) -> List[Dict]:
        if not hasattr(self.session_state, 'distribucion_data'):
            st.toast("🚨 No se encontraron datos de distribución", icon="⚠️")
            return []

        config = self.session_state.distribucion_data.get('arrays_config', [])
        if not isinstance(config, list):
            st.error("Formato inválido en configuración de arrays")
            return []

        valid_arrays = []
        for array in config:
            if all(key in array for key in [
                'largo_fila', 'filas_x_columna', 'columnas',
                'total_filas_array', 'paneles_por_fila'
            ]):
                valid_arrays.append(array)

        if len(valid_arrays) != len(config):
            st.toast("Algunos arrays tienen configuración incompleta", icon="⚠️")

        return valid_arrays

    def calcular_materiales_array(self, array_config: Dict) -> Dict:
        """Calcula los materiales necesarios para un array solar específico"""
        try:
            # Cálculo de materiales para UN array específico
            mounting_rail = math.ceil(
                array_config['largo_fila'] * 2 * 
                array_config['filas_x_columna'] * 
                array_config['columnas']
            )

            end_clamps = 4 * array_config['total_filas_array']
            
            mid_clamps = max(0,
                (array_config['paneles_por_fila'] - 1) * 
                2 * array_config['total_filas_array']
            )

            return {
                'mounting_rail': mounting_rail,
                'end_clamps': end_clamps,
                'mid_clamps': mid_clamps,
                'roof_clamps': array_config['paneles_por_fila'] * array_config['total_filas_array'],
                'ground_lug': array_config['paneles_por_fila'] * array_config['total_filas_array'],
                'configuracion': (
                    f"{array_config['filas_x_columna']}x{array_config['columnas']} "
                    f"({array_config['total_filas_array']} filas totales)"
                )
            }
        except KeyError as e:
            st.error(f"Falta clave en configuración del array: {str(e)}")
            return {}
        except Exception as e:
            st.error(f"Error en cálculo de materiales: {str(e)}")
            return {}

    def mostrar_materiales_por_array(self):
        try:
            config_arrays = self.session_state.distribucion_data.get('arrays_config', [])
        
            if not config_arrays:
                st.warning("Configure primero los arrays en Distribución Solar")
                return

            st.subheader("Materiales por Array")

            with st.container():
                cols = st.columns(2)
                for i in range(len(config_arrays)):
                    array_config = config_arrays[i]
                    materiales = self.calcular_materiales_array(array_config)

                    # Asignar materiales al array en session_state sin sobrescribirlo
                    self.session_state.distribucion_data['arrays_config'][i]['materiales'] = materiales

                    with cols[i % 2]:
                        with st.container(border=True):
                            st.markdown(f"""
                            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                <div style="font-size: 1.2rem; font-weight: bold;">Array {i+1}</div>
                                <div style="margin-left: auto; background-color: #e8f4fc; 
                                    padding: 0.2rem 0.5rem; border-radius: 0.5rem; 
                                    font-size: 0.8rem;">
                                    {array_config.get('ubicacion', 'Posición no especificada')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            html_content = f"""
                            <table class="materiales-table">
                                <tr>
                                    <th style="width: 40%;">Componente</th>
                                    <th style="width: 30%; text-align: center;">Cantidad</th>
                                    <th style="width: 30%; text-align: center;">Unidad</th>
                                </tr>
                                <tr><td>Mounting Rail</td><td style="text-align: center;">{materiales['mounting_rail']}</td><td style="text-align: center;">metros</td></tr>
                                <tr><td>End Clamps</td><td style="text-align: center;">{materiales['end_clamps']}</td><td style="text-align: center;">unidades</td></tr>
                                <tr><td>Mid Clamps</td><td style="text-align: center;">{materiales['mid_clamps']}</td><td style="text-align: center;">unidades</td></tr>
                                <tr><td>Roof Clamps</td><td style="text-align: center;">{materiales['roof_clamps']}</td><td style="text-align: center;">unidades</td></tr>
                                <tr><td>Round Lug</td><td style="text-align: center;">{materiales['ground_lug']}</td><td style="text-align: center;">unidades</td></tr>
                            </table>
                            <style>
                            .materiales-table {{
                                width: 100%;
                                border-collapse: collapse;
                                margin: 1rem 0;
                                font-family: Arial, sans-serif;
                            }}
                            .materiales-table th {{
                                background-color: #2c3e50;
                                color: white;
                                border: 1px solid #34495e;
                                padding: 0.75rem;
                            }}
                            .materiales-table td {{
                                border: 1px solid #dee2e6;
                                padding: 0.75rem;
                            }}
                            .materiales-table tr:nth-child(even) {{
                                background-color: #f8f9fa;
                            }}
                            </style>
                            """
                            st.markdown(html_content, unsafe_allow_html=True)



                            


                            with st.expander(f"Detalles técnicos Array {i+1}"):
                                st.write(f"Paneles por fila: {array_config.get('paneles_por_fila', 0)}")
                                st.write(f"Filas por columna: {array_config.get('filas_x_columna', 0)}")
                                st.write(f"Columnas totales: {array_config.get('columnas', 0)}")
        except Exception as e:
            st.error(f"Error al mostrar materiales: {str(e)}")


    # Método temporal para evitar el error
    def mostrar_calculos_estructura(self, panel_data: Dict):
        """Placeholder para futuros cálculos de estructura"""
        pass                               
    def mostrar_total_materiales(self):
        """Muestra un resumen con el total de materiales de todos los arrays"""
        try:
            if not hasattr(self.session_state, 'distribucion_data'):
                st.warning("No se encontró la configuración de distribución solar.")
                return

            config_arrays = self.session_state.distribucion_data.get('arrays_config', [])
            if not config_arrays:
                st.warning("No hay arrays configurados. Ve a la pestaña 'Distribución Solar'.")
                return

            # Recalcular materiales si no existen
            for i, array in enumerate(config_arrays):
                if "materiales" not in array:
                    materiales = self.calcular_materiales_array(array)
                    self.session_state.distribucion_data['arrays_config'][i]['materiales'] = materiales

            # Precios unitarios FOB CH
            precios_fob = {
                'mounting_rail': 24.40,
                'end_clamps': 0.31,
                'mid_clamps': 0.32,
                'roof_clamps': 1.03,
                'ground_lug': 0.08
            }

            pesos_unitarios = {
                'mounting_rail': 10.2,
                'end_clamps': 0.055,
                'mid_clamps': 0.055,
                'roof_clamps': 0.25,
                'ground_lug': 0.1
            }

            conver_mounting = 4.65

            totales = {
                'mounting_rail': 0,
                'end_clamps': 0,
                'mid_clamps': 0,
                'roof_clamps': 0,
                'ground_lug': 0
            }

            for array in config_arrays:
                for material, cantidad in array['materiales'].items():
                    if material in totales:
                        totales[material] += cantidad

            cantidad_mounting = math.ceil(totales['mounting_rail'] / conver_mounting)

            peso_total = (
                (pesos_unitarios['mounting_rail'] * cantidad_mounting) +
                (pesos_unitarios['end_clamps'] * totales['end_clamps']) +
                (pesos_unitarios['mid_clamps'] * totales['mid_clamps']) +
                (pesos_unitarios['roof_clamps'] * totales['roof_clamps']) +
                (pesos_unitarios['ground_lug'] * totales['ground_lug'])
            )

            total_mounting = precios_fob['mounting_rail'] * cantidad_mounting
            total_end_clamps = precios_fob['end_clamps'] * totales['end_clamps']
            total_mid_clamps = precios_fob['mid_clamps'] * totales['mid_clamps']
            total_roof_clamps = precios_fob['roof_clamps'] * totales['roof_clamps']
            total_ground_lug = precios_fob['ground_lug'] * totales['ground_lug']

            gran_total = (
                total_mounting +
                total_end_clamps +
                total_mid_clamps +
                total_roof_clamps +
                total_ground_lug
            )

            self.session_state["fob_ch_estructura_solar"] = gran_total

            with st.container(border=True):
                st.subheader("Total de Materiales")
            
                html_content = f"""
                <table class="total-materiales-table">
                    <thead>
                        <tr>
                            <th rowspan="2">Componentes</th>
                            <th rowspan="2">Cant.</th>
                            <th rowspan="2">Medida</th>
                            <th rowspan="2">Conver</th>
                            <th rowspan="2">Peso</th>
                            <th rowspan="2">Cantidad</th>
                            <th rowspan="2">FOB CH</th>
                            <th rowspan="2">TOTAL</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Mounting Rail</td>
                            <td>{totales['mounting_rail']}</td>
                            <td>Metros</td>
                            <td>{conver_mounting}</td>
                            <td>{pesos_unitarios['mounting_rail']}</td>
                            <td>{cantidad_mounting}</td>
                            <td>${precios_fob['mounting_rail']:.2f}</td>
                            <td>${total_mounting:.2f}</td>
                        </tr>
                        <tr>
                            <td>End Clamps</td>
                            <td>{totales['end_clamps']}</td>
                            <td>Units</td>
                            <td></td>
                            <td>{pesos_unitarios['end_clamps']:.3f}</td>
                            <td></td>
                            <td>${precios_fob['end_clamps']:.2f}</td>
                            <td>${total_end_clamps:.2f}</td>
                        </tr>
                        <tr>
                            <td>Mid Clamps</td>
                            <td>{totales['mid_clamps']}</td>
                            <td>Units</td>
                            <td></td>
                            <td>{pesos_unitarios['mid_clamps']:.3f}</td>
                            <td></td>
                            <td>${precios_fob['mid_clamps']:.2f}</td>
                            <td>${total_mid_clamps:.2f}</td>
                        </tr>
                        <tr>
                            <td>Roof Clamps</td>
                            <td>{totales['roof_clamps']}</td>
                            <td>Units</td>
                            <td></td>
                            <td>{pesos_unitarios['roof_clamps']:.2f}</td>
                            <td></td>
                            <td>${precios_fob['roof_clamps']:.2f}</td>
                            <td>${total_roof_clamps:.2f}</td>
                        </tr>
                        <tr>
                            <td>Ground Lug</td>
                            <td>{totales['ground_lug']}</td>
                            <td>Units</td>
                            <td></td>
                            <td>{pesos_unitarios['ground_lug']:.1f}</td>
                            <td></td>
                            <td>${precios_fob['ground_lug']:.2f}</td>
                            <td>${total_ground_lug:.2f}</td>
                        </tr>
                        <tr style="font-weight: bold; background-color: #f0f0f0;">
                            <td colspan="4"></td>
                            <td>Peso Total</td>
                            <td>{peso_total:.2f}</td>
                            <td>TOTAL</td>
                            <td>${gran_total:.2f}</td>
                        </tr>
                    </tbody>
                </table>
                <style>
                .total-materiales-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 1rem 0;
                    font-family: Arial, sans-serif;
                    font-size: 0.9rem;
                }}
                .total-materiales-table th {{
                    background-color: #2c3e50;
                    color: white;
                    border: 1px solid #34495e;
                    padding: 0.5rem;
                    text-align: center;
                }}
                .total-materiales-table td {{
                    border: 1px solid #dee2e6;
                    padding: 0.5rem;
                    text-align: center;
                }}
                .total-materiales-table tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                </style>
                """
                st.markdown(html_content, unsafe_allow_html=True)


            df_total = pd.DataFrame([
                {
                    "Componentes": "Mounting Rail",
                    "Cant.": cantidad_mounting,
                    "FOB CH": precios_fob['mounting_rail'],
                    "Total": total_mounting
                },
                {
                    "Componentes": "End Clamps",
                    "Cant.": totales["end_clamps"],
                    "FOB CH": precios_fob['end_clamps'],
                    "Total": total_end_clamps
                },
                {
                    "Componentes": "Mid Clamps",
                    "Cant.": totales["mid_clamps"],
                    "FOB CH": precios_fob['mid_clamps'],
                    "Total": total_mid_clamps
                },
                {
                    "Componentes": "Roof Clamps",
                    "Cant.": totales["roof_clamps"],
                    "FOB CH": precios_fob['roof_clamps'],
                    "Total": total_roof_clamps
                },
                {
                    "Componentes": "Ground Lug",
                    "Cant.": totales["ground_lug"],
                    "FOB CH": precios_fob['ground_lug'],
                    "Total": total_ground_lug
                },
            ])

            self.session_state["estructura_total_materiales"] = df_total

        except Exception as e:
            st.error(f"Error al calcular total de materiales: {str(e)}")