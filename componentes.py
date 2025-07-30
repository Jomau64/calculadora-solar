import streamlit as st
import pandas as pd

class ComponentesManager:
    def __init__(self, session_state):
        self.session_state = session_state

    def mostrar_pestana(self):
        st.header("📦 Componentes")

        self._mostrar_componentes_principales()
        st.divider()
        self._mostrar_estructura_solar()
        st.divider()
        self._mostrar_proteccion_conexion()
        st.divider()
        self._mostrar_cables()

    def _mostrar_componentes_principales(self):
        panel_sel = self.session_state.equipamiento_seleccionado.get("Paneles Solares", "No seleccionado")
        inversor_sel = self.session_state.equipamiento_seleccionado.get("Inversores", "No seleccionado")
        total_paneles = int(self.session_state.get("distribucion_data", {}).get("total_paneles", 0))
        datos_cadenas = self.session_state.get("datos_distribucion_cadenas", {})
        cantidad_inversores = int(datos_cadenas.get("cantidad_inversores", 0))

        # Capacidad del panel e inversor
        capacidad_panel_watts = 0
        capacidad_inversor_kw = 0

        df_paneles = self.session_state.manager_equipamiento.df_equipamientos.get("Paneles Solares", pd.DataFrame())
        df_inversores = self.session_state.manager_equipamiento.df_equipamientos.get("Inversores", pd.DataFrame())

        if not df_paneles.empty and panel_sel in df_paneles["nombre_display"].values:
            try:
                capacidad_panel_watts = float(df_paneles.loc[df_paneles["nombre_display"] == panel_sel, "Watts"].values[0])
            except:
                capacidad_panel_watts = 0

        if not df_inversores.empty and inversor_sel in df_inversores["nombre_display"].values:
            try:
                capacidad_inversor_kw = float(df_inversores.loc[df_inversores["nombre_display"] == inversor_sel, "Potencia Salida"].values[0]) / 1000
            except:
                capacidad_inversor_kw = 0

        capacidad_kwp = round((total_paneles * capacidad_panel_watts) / 1000, 2)
        capacidad_kw = round((cantidad_inversores * capacidad_inversor_kw), 2)

        def celda(valor):
            return f"<td style='text-align:center; vertical-align:middle'>{valor}</td>"

        html = f"""
        <div style='font-weight:bold; font-size:20px; margin-bottom:10px;'>Componentes Principales</div>
        <table style='width:100%; border-collapse:collapse; font-size:16px;'>
            <thead>
                <tr style='background-color:#004d00; color:white'>
                    <th style='text-align:left;'>Componentes Principales</th>
                    <th style='text-align:center;'>Descripción</th>
                    <th style='text-align:center;'>Cantidad</th>
                </tr>
            </thead>
            <tbody>
                <tr style='background-color:#e6f2e6;'>
                    <td>Paneles Solares</td>{celda(panel_sel)}{celda(f"{total_paneles} Paneles")}
                </tr>
                <tr>
                    <td>Inversores</td>{celda(inversor_sel)}{celda(f"{cantidad_inversores} Inversores")}
                </tr>
                <tr style='background-color:#e6f2e6;'>
                    <td>Baterías de almacenamiento</td>{celda("No seleccionado")}{celda("0 Baterías")}
                </tr>
                <tr>
                    <td>Convertidor de alto voltaje DC</td>{celda("No seleccionado")}{celda("0")}
                </tr>
                <tr style='background-color:#e6f2e6;'>
                    <td>Controladores de carga MPPT</td>{celda("No seleccionado")}{celda("0")}
                </tr>
            </tbody>
        </table>
        """
        st.markdown(html, unsafe_allow_html=True)

        self.session_state["componentes_principales"] = {
            "paneles": total_paneles,
            "inversores": cantidad_inversores,
            "capacidad_kwp": capacidad_kwp,
            "capacidad_kw": capacidad_kw,
            "Paneles Solares": total_paneles,
            "Inversores": cantidad_inversores,
            "Baterías de almacenamiento": 0,
            "Convertidor de alto voltaje DC": 0,
            "Controladores de carga MPPT": 0
        }

    def _mostrar_estructura_solar(self):
        st.markdown("<div style='font-weight:bold; font-size:20px;'>Estructura Solar</div><br>", unsafe_allow_html=True)

        componentes = {
            "Mounting Rail": 0,
            "End Clamps": 0,
            "Mid Clamps": 0,
            "Roof Clamps": 0,
            "Ground Lug": 0
        }

        df = self._obtener_datos_estructura()
        if not df.empty:
            for nombre in componentes.keys():
                match = df[df["Componentes"].str.lower().str.contains(nombre.lower(), na=False)]
                if not match.empty:
                    try:
                        componentes[nombre] = int(pd.to_numeric(match["Cant."], errors="coerce").sum())
                    except:
                        componentes[nombre] = 0

        html = """
        <table style='width:100%; border-collapse:collapse; font-size:16px;'>
            <thead>
                <tr style='background-color:#004d00; color:white'>
                    <th style='text-align:left;'>Componente</th>
                    <th style='text-align:center;'>Descripción</th>
                    <th style='text-align:center;'>Cantidad</th>
                </tr>
            </thead>
            <tbody>
        """
        for i, (k, v) in enumerate(componentes.items()):
            bg = "#e6f2e6" if i % 2 == 0 else "white"
            html += f"<tr style='background-color:{bg};'><td>{k}</td><td style='text-align:center;'>-</td><td style='text-align:center;'>{v}</td></tr>"

        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)

    def _mostrar_proteccion_conexion(self):
        st.markdown("<div style='font-weight:bold; font-size:20px;'>Protección y Conexión</div><br>", unsafe_allow_html=True)

        filas = [
            "Breaker DC", "Breaker AC", "Protección Sobre Tensión AC", "Protección Sobre Tensión DC",
            "Caja Combinadora PV", "Caja de Unión", "Interruptor PV DC", "Interruptor AC",
            "Tablero de Distribución", "Transfer Automático"
        ]

        html = """
        <table style='width:100%; border-collapse:collapse; font-size:16px;'>
            <thead>
                <tr style='background-color:#004d00; color:white'>
                    <th style='text-align:left;'>Protección y Conexión</th>
                    <th style='text-align:center;'>Descripción</th>
                    <th style='text-align:center;'>Cantidad</th>
                </tr>
            </thead>
            <tbody>
        """
        for i, item in enumerate(filas):
            bg = "#e6f2e6" if i % 2 == 0 else "white"
            html += f"<tr style='background-color:{bg};'><td>{item}</td><td style='text-align:center;'>-</td><td style='text-align:center;'>0</td></tr>"

        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)

    def _mostrar_cables(self):
        st.markdown("<div style='font-weight:bold; font-size:20px;'>Cables</div><br>", unsafe_allow_html=True)

        filas = [
            "Cable PV Rojo", "Cable PV Negro", "Conector MC4 Macho", "Conector MC4 Hembra",
            "Cable AC Negro", "Cable AC Blanco", "Cable AC Amarillo", "Cable AC Verde", "Cable RS485"
        ]

        html = """
        <table style='width:100%; border-collapse:collapse; font-size:16px;'>
            <thead>
                <tr style='background-color:#004d00; color:white'>
                    <th style='text-align:left;'>Cables</th>
                    <th style='text-align:center;'>Descripción</th>
                    <th style='text-align:center;'>Cantidad</th>
                </tr>
            </thead>
            <tbody>
        """
        for i, item in enumerate(filas):
            bg = "#e6f2e6" if i % 2 == 0 else "white"
            html += f"<tr style='background-color:{bg};'><td>{item}</td><td style='text-align:center;'>-</td><td style='text-align:center;'>0</td></tr>"

        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)

    def _obtener_datos_estructura(self):
        if "estructura_total_materiales" not in self.session_state:
            return pd.DataFrame()
        df = self.session_state.estructura_total_materiales
        if not isinstance(df, pd.DataFrame) or df.empty:
            return pd.DataFrame()
        if "Componentes" not in df.columns or "Cant." not in df.columns:
            return pd.DataFrame()
        return df
