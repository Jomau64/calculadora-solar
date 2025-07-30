import streamlit as st
import pandas as pd
import locale
import math
from difflib import get_close_matches

class Generacion:
    def __init__(self, session_state):
        self.session_state = session_state
        locale.setlocale(locale.LC_ALL, '')

    def mostrar_pestana(self):
        st.header("⚡ Generación")

        dias_actuales = self._obtener_dias_facturados()
        if "dias_facturados_previos" not in self.session_state:
            self.session_state["dias_facturados_previos"] = dias_actuales
        elif dias_actuales != self.session_state["dias_facturados_previos"]:
            self.session_state["dias_facturados_previos"] = dias_actuales
            st.rerun()

        panel_data = self._obtener_datos_panel()
        if panel_data['panel'] is None:
            return

        with st.expander("🔍 Configuración Actual", expanded=True):
            st.markdown(f"""
            **Panel seleccionado:** `{panel_data['panel']}`  
            **NOCT utilizado:** `{panel_data['noct']}` kWh (valor redondeado)  
            **Días facturados:** `{panel_data['dias_facturados']}` días  
            **Horas pico diarias:** `5.5` h
            """)

        tabla_disponibilidad = self._generar_y_mostrar_tabla(panel_data)
        self._mostrar_cuadro_consumo_generacion(panel_data['dias_facturados'], panel_data['noct'], tabla_disponibilidad)
        self._mostrar_cuadro_baterias()

    def _obtener_datos_panel(self):
        result = {
            'panel': None,
            'noct': 0,
            'dias_facturados': 30,
            'arrays_config': []
        }

        try:
            if not hasattr(self.session_state, 'manager_equipamiento'):
                st.error("Error: No se puede acceder a los datos de Equipamientos")
                return result

            panel_seleccionado = self.session_state.equipamiento_seleccionado.get("Paneles Solares", "").strip()
            if not panel_seleccionado:
                st.error("Error: No se ha seleccionado ningún panel solar")
                return result

            df_paneles = self.session_state.manager_equipamiento.df_equipamientos.get("Paneles Solares", pd.DataFrame())
            if df_paneles.empty:
                st.error("Error: No hay datos de paneles solares")
                return result

            panel_info = self._buscar_panel(df_paneles, panel_seleccionado)
            if panel_info is None:
                return result

            noct = float(panel_info['NOCT'].values[0])
            result['noct'] = math.ceil(noct) if noct != int(noct) else int(noct)
            result['dias_facturados'] = self._obtener_dias_facturados()
            result['arrays_config'] = self.session_state.distribucion_data.get("arrays_config", [])
            result['panel'] = panel_info['Modelo'].values[0]

            return result

        except Exception as e:
            st.error(f"Error al obtener datos: {str(e)}")
            return result

    def _buscar_panel(self, df_paneles, panel_buscado):
        paneles_normalizados = df_paneles['Modelo'].str.strip().str.lower()
        panel_buscado_clean = panel_buscado.strip().lower()

        marcas = ["jinko", "longi", "trina", "canadian", "sunpower"]
        for marca in marcas:
            if panel_buscado_clean.startswith(marca):
                panel_buscado_clean = panel_buscado_clean.replace(marca, '').strip()

        paneles_sin_marcas = paneles_normalizados.apply(
            lambda x: x.replace("jinko", "").replace("longi", "").replace("trina", "").replace("canadian", "").replace("sunpower", "").strip()
        )

        match_index = paneles_sin_marcas[paneles_sin_marcas == panel_buscado_clean].index
        if not match_index.empty:
            return df_paneles.loc[match_index]

        modelos = df_paneles['Modelo'].tolist()
        matches = get_close_matches(panel_buscado, modelos, n=1, cutoff=0.8)
        if matches:
            if matches[0].strip().lower() != panel_buscado_clean:
                st.warning(f"Panel '{panel_buscado}' no encontrado. Usando '{matches[0]}'")
            return df_paneles[df_paneles['Modelo'] == matches[0]]

        st.error(f"Panel '{panel_buscado}' no encontrado en la base de datos")
        self._mostrar_paneles_disponibles(df_paneles)
        return None

    def _mostrar_paneles_disponibles(self, df_paneles):
        with st.expander("📋 Paneles disponibles"):
            st.dataframe(df_paneles[['Modelo', 'NOCT']] if 'NOCT' in df_paneles.columns else df_paneles)

    def _obtener_dias_facturados(self):
        try:
            valor = self.session_state['cliente_data'].get("Días Facturados", "30")
            if pd.isna(valor) or not str(valor).strip().isdigit():
                return 30
            return int(valor)
        except:
            return 30

    def _mostrar_cuadro_consumo_generacion(self, dias_facturados, noct, disponibilidad_tabla):
        consumo_data = self.session_state.get('consumo_data', {})
        horarios = {
            'A': "08h00-18h00",
            'B': "18h00-22h00",
            'C': "22h00-08h00",
            'D': "S,D,F 18h00-22h00"
        }
        tabla = []
        total_consumo = total_generacion = total_gen_5h = 0
        gen_x_5h_A = gen_x_5h_B = 0

        for h in ['A', 'B', 'C', 'D']:
            kwh_str = consumo_data.get(f"kW/h {h}", "").replace(",", ".")
            if not kwh_str:
                continue
            try:
                kwh_total = float(kwh_str)
            except:
                kwh_total = 0

            consumo_diario = kwh_total / dias_facturados if dias_facturados else 0
            generacion = math.floor(consumo_diario * 1.05)
            gen_5h = math.floor(generacion / 5)

            total_consumo += consumo_diario
            total_generacion += generacion
            total_gen_5h += gen_5h

            if h == 'A': gen_x_5h_A = gen_5h
            if h == 'B': gen_x_5h_B = gen_5h

            tabla.append({
                "Consumo por Horario": f"Energía act. horario {h} ({horarios[h]})",
                "Consumo Diario": f"{round(consumo_diario)} kWh",
                "Generación Solar Requerida": f"{generacion} kWh",
                "Gen X 5 horas": f"{gen_5h} kWh"
            })

        tabla.append({
            "Consumo por Horario": "",
            "Consumo Diario": f"**{math.floor(total_consumo)} kWh**",
            "Generación Solar Requerida": f"**{total_generacion} kWh**",
            "Gen X 5 horas": f"**{total_gen_5h} kWh**"
        })

        st.subheader("📘 Consumo y Generación")
        st.dataframe(pd.DataFrame(tabla), use_container_width=True, hide_index=True)

        total_paneles = disponibilidad_tabla['total_paneles']
        kwh_disponible = (total_paneles * noct) / 1000
        kwh_pico = gen_x_5h_A + gen_x_5h_B
        kwh_netmetering = total_gen_5h
        paneles_pico = math.ceil((kwh_pico * 1000) / noct) if noct else 0
        paneles_net = math.ceil((kwh_netmetering * 1000) / noct) if noct else 0

        df_cobertura = pd.DataFrame({
            "": ["kWh Necesarios", "Paneles Necesarios"],
            "Disponible": [f"{round(kwh_disponible)} kW", f"{total_paneles} Paneles"],
            "Cubre Demanda Horarios Pico": [f"{kwh_pico} kWh", f"{paneles_pico} Paneles"],
            "Cubre NetMetering": [f"{kwh_netmetering} kWh", f"{paneles_net} Paneles"]
        })

        st.subheader("🌞 Necesidad de Cobertura de Paneles Solares")
        st.dataframe(df_cobertura, use_container_width=True, hide_index=True)

    def _mostrar_cuadro_baterias(self):
        try:
            respaldo_kwh = float(
                self.session_state.get('requerimiento_data', {})
                    .get("Respaldo (4 Horas de Respaldo)_ideal", "0").replace(",", ".")
            )
        except:
            respaldo_kwh = 0
        baterias_necesarias = 0
        df_baterias = pd.DataFrame({
            "": ["kWh", "Baterías Necesarias"],
            "Respaldo de 4 Horas": [f"{int(round(respaldo_kwh))} kWh", f"{baterias_necesarias} Baterías"]
        })
        st.subheader("🔋 Necesidad de Cobertura de Baterías")
        st.dataframe(df_baterias, use_container_width=True, hide_index=True)

    def _generar_y_mostrar_tabla(self, panel_data):
        try:
            HORAS_PICO = 5.5
            tabla = []
            totales = {'kWh': 0, 'kWd': 0, 'kWm': 0, 'paneles': 0}
            for i in range(8):
                array_info = self._calcular_array_info(i, panel_data, HORAS_PICO)
                tabla.append(array_info['fila'])
                for key in totales:
                    totales[key] += array_info['valores'].get(key, 0)

            tabla.append({
                "Zonas": "TOTAL",
                "kWh": self._formatear_numero(totales['kWh']),
                "kWd": self._formatear_numero(totales['kWd']),
                "kWm": self._formatear_numero(totales['kWm']),
                "Capacidad de Paneles": totales['paneles']
            })

            st.subheader("📊 Disponibilidad")
            st.dataframe(
                pd.DataFrame(tabla),
                use_container_width=True,
                hide_index=True
            )

            # ✅ Guardar kWm total en session_state
            if "generacion_data" not in self.session_state:
                self.session_state["generacion_data"] = {}
            self.session_state["generacion_data"]["kWm"] = round(totales['kWm'], 2)

            
            return {'total_paneles': totales['paneles']}
        except Exception as e:
            st.error(f"Error al generar la tabla: {str(e)}")
            return {'total_paneles': 0}

    def _calcular_array_info(self, index, panel_data, horas_pico):
        nombre = f"Array {index+1}"
        if index < len(panel_data['arrays_config']):
            paneles = panel_data['arrays_config'][index].get("paneles_array", 0)
            valores = {
                'kWh': (paneles * panel_data['noct']) / 1000,
                'kWd': (paneles * panel_data['noct'] * horas_pico) / 1000,
                'kWm': (paneles * panel_data['noct'] * horas_pico * panel_data['dias_facturados']) / 1000,
                'paneles': paneles
            }


            # Guardar kWm en session_state para Análisis Económico
            if "generacion_data" not in self.session_state:
                self.session_state["generacion_data"] = {}

            self.session_state["generacion_data"]["kWm"] = round(valores["kWm"], 2) 


        else:
            valores = {'kWh': 0, 'kWd': 0, 'kWm': 0, 'paneles': 0}

        return {
            'fila': {
                "Zonas": nombre,
                "kWh": self._formatear_numero(valores['kWh']),
                "kWd": self._formatear_numero(valores['kWd']),
                "kWm": self._formatear_numero(valores['kWm']),
                "Capacidad de Paneles": valores['paneles']
            },
            'valores': valores
        }

    def _formatear_numero(self, valor):
        if isinstance(valor, (int, float)):
            if valor == 0:
                return "-"
            try:
                return f"{valor:.2f}"
            except:
                return str(valor)
        return valor
