import streamlit as st
import pandas as pd

class AnalisisEconomico:
    def __init__(self, session_state):
        self.session_state = session_state

    def mostrar_pestana(self):
        st.header("📊 Análisis Económico")
        self.mostrar_consumo_energetico()
        st.divider()
        self.mostrar_recomendacion()
        st.divider()
        self.mostrar_sistema_hibrido()
        self.mostrar_cuadro_inversion()
        self.mostrar_bloque_analisis_economico()
        self.mostrar_bloque_roi()

    def convertir_a_float(self, valor):
        try:
            return float(str(valor).replace(",", "").strip())
        except (ValueError, TypeError):
            return 0.0

    def mostrar_consumo_energetico(self):
        datos = self.session_state.get("consumo_data", {})
        if not datos:
            st.warning("No hay datos de consumo energético disponibles.")
            return

        try:
            def safe_div(a, b):
                return round(a / b, 5) if b else 0.0

            consumo = []
            for etiqueta, clave_kw, clave_total in [
                ("Energía act. horario A (8h00-18h00)", "kW/h A", "Total A"),
                ("Energía act. horario B (18h00-22h00)", "kW/h B", "Total B"),
                ("Energía act. horario C (22h00-08h00)", "kW/h C", "Total C"),
                ("Energía act. horario D (S,D,F 18h00-22h00)", "kW/h D", "Total D")
            ]:
                kwh = self.convertir_a_float(datos.get(clave_kw))
                total = self.convertir_a_float(datos.get(clave_total))
                costo_kwh = safe_div(total, kwh)
                consumo.append((etiqueta, costo_kwh, kwh, total))

            demanda_kwh = self.convertir_a_float(datos.get("kW/h Demanda"))
            demanda_costo = self.convertir_a_float(datos.get("Total Demanda"))
            demanda_costo_kwh = safe_div(demanda_costo, demanda_kwh)

            total_kwh = sum(x[2] for x in consumo)
            total_usd = sum(x[3] for x in consumo) + demanda_costo

            filas_html = ""
            for fila in consumo:
                filas_html += f"<tr><td>{fila[0]}</td><td>{fila[1]:.3f}</td><td>{int(fila[2])}</td><td>{fila[3]:.2f}</td></tr>"
            filas_html += f"<tr><td>Demanda Facturable</td><td>{demanda_costo_kwh:.3f}</td><td>{int(demanda_kwh)}</td><td>{demanda_costo:.2f}</td></tr>"
            filas_html += f"<tr><td></td><td></td><td><b>{int(total_kwh)}</b></td><td><b>{total_usd:.2f}</b></td></tr>"

            html = f"""
            <h4>Consumo Energético</h4>
            <table style='width:100%; border-collapse: collapse; font-size: 16px;'>
                <thead>
                    <tr style='background-color: #f0f0f0; font-weight: bold;'>
                        <td style='border: 1px solid #ccc; padding: 6px;'>Periodo</td>
                        <td style='border: 1px solid #ccc; padding: 6px;'>Costo x kWh</td>
                        <td style='border: 1px solid #ccc; padding: 6px;'>kWh</td>
                        <td style='border: 1px solid #ccc; padding: 6px;'>Total ($)</td>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
            """
            st.markdown(html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al mostrar consumo energético: {e}")

    def mostrar_recomendacion(self):
        componentes = self.session_state.get("componentes_principales", {})
        equipo = self.session_state.get("equipamiento_seleccionado", {})
        df_paneles = self.session_state.manager_equipamiento.df_equipamientos.get("Paneles Solares", None)
        df_inversores = self.session_state.manager_equipamiento.df_equipamientos.get("Inversores", None)

        panel_nombre = equipo.get("Paneles Solares", "")
        inversor_nombre = equipo.get("Inversores", "")

        cantidad_paneles = componentes.get("paneles", 0)
        cantidad_inversores = componentes.get("inversores", 0)

        capacidad_panel = "-"
        capacidad_inversor = "-"
        total_kw_panel = "-"
        total_kw_inversor = "-"

        if df_paneles is not None and panel_nombre in df_paneles["nombre_display"].values:
            fila_panel = df_paneles[df_paneles["nombre_display"] == panel_nombre].iloc[0]
            cap_raw = str(fila_panel.get("Capacidad", "")).replace(",", "").replace(" W", "").strip()
            try:
                cap_w = float(cap_raw)
                capacidad_panel = f"{int(cap_w)} W"
                total_kw_panel = f"{round((cantidad_paneles * cap_w) / 1000)} kW"
            except:
                pass

        if df_inversores is not None and inversor_nombre in df_inversores["nombre_display"].values:
            fila_inv = df_inversores[df_inversores["nombre_display"] == inversor_nombre].iloc[0]
            cap_raw = str(fila_inv.get("Capacidad", "")).replace(",", "").replace(" kW", "").strip()
            try:
                cap_inv = float(cap_raw)
                capacidad_inversor = f"{int(cap_inv)} kW" if cap_inv.is_integer() else f"{cap_inv:.2f} kW"
                total_kw_inversor = f"{round(cantidad_inversores * cap_inv)} kW"
            except:
                pass

        st.markdown("#### Recomendación")

        html = f"""
        <table style='width:100%; border-collapse: collapse; font-size: 16px;'>
            <thead>
                <tr style='background-color: #f0f0f0; font-weight: bold;'>
                    <td style='padding: 8px; border: 1px solid #ccc;'>Equipos</td>
                    <td style='padding: 8px; border: 1px solid #ccc;'>Cantidad</td>
                    <td style='padding: 8px; border: 1px solid #ccc;'>Capacidad</td>
                    <td style='padding: 8px; border: 1px solid #ccc;'>Total</td>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style='padding: 8px; border: 1px solid #ccc;'>Paneles Solares</td>
                    <td style='padding: 8px; border: 1px solid #ccc;'>{cantidad_paneles}</td>
                    <td style='padding: 8px; border: 1px solid #ccc;'>{capacidad_panel}</td>
                    <td style='padding: 8px; border: 1px solid #ccc;'>{total_kw_panel}</td>
                </tr>
                <tr>
                    <td style='padding: 8px; border: 1px solid #ccc;'>Inversores de alto voltaje</td>
                    <td style='padding: 8px; border: 1px solid #ccc;'>{cantidad_inversores}</td>
                    <td style='padding: 8px; border: 1px solid #ccc;'>{capacidad_inversor}</td>
                    <td style='padding: 8px; border: 1px solid #ccc;'>{total_kw_inversor}</td>
                </tr>
            </tbody>
        </table>
        """
        st.markdown(html, unsafe_allow_html=True)

    def mostrar_sistema_hibrido(self):
        consumo_data = self.session_state.get("consumo_data", {})
        generacion_data = self.session_state.get("generacion_data", {})

        kwh_total = sum([
            self.convertir_a_float(consumo_data.get("kW/h A")),
            self.convertir_a_float(consumo_data.get("kW/h B")),
            self.convertir_a_float(consumo_data.get("kW/h C")),
            self.convertir_a_float(consumo_data.get("kW/h D"))
        ])

        total_usd = sum([
            self.convertir_a_float(consumo_data.get("Total A")),
            self.convertir_a_float(consumo_data.get("Total B")),
            self.convertir_a_float(consumo_data.get("Total C")),
            self.convertir_a_float(consumo_data.get("Total D")),
            self.convertir_a_float(consumo_data.get("Total Demanda"))
        ])

        produccion_kwh_solar = self.convertir_a_float(
            str(generacion_data.get("kWm", "")).replace("kWh", "").strip()
        )
        # Manejo de división por cero
        totalA = self.convertir_a_float(consumo_data.get("Total A"))
        kwhA = self.convertir_a_float(consumo_data.get("kW/h A"))
        costo_horario_a = totalA / kwhA if kwhA else 0
        valor_mensual_solar = round(produccion_kwh_solar * costo_horario_a, 2)

        html = f"""
        <br><h4 style='color:#014421;'>Sistema híbrido de producción eléctrica</h4>
        <table style='width:100%; border-collapse: collapse; font-size: 16px;'>
            <thead>
                <tr style='background-color:#014421; color:white;'>
                    <th style='padding: 6px; border: 1px solid #ccc;'> </th>
                    <th style='padding: 6px; border: 1px solid #ccc;'>Emp. Eléctrica</th>
                    <th style='padding: 6px; border: 1px solid #ccc;'>Producción Solar</th>
                </tr>
            </thead>
            <tbody>
                <tr style='background-color:#eafae6;'>
                    <td style='padding: 6px; border: 1px solid #ccc;'>Producción mensual (promedio anual) en kW/h</td>
                    <td style='padding: 6px; border: 1px solid #ccc;'>{int(kwh_total)} kWh</td>
                    <td style='padding: 6px; border: 1px solid #ccc;'>{int(produccion_kwh_solar)} kWh</td>
                </tr>
                <tr style='background-color:#eafae6;'>
                    <td style='padding: 6px; border: 1px solid #ccc;'>Valor mensual (promedio anual) en dólares</td>
                    <td style='padding: 6px; border: 1px solid #ccc; color:darkred;'>${total_usd:.2f}</td>
                    <td style='padding: 6px; border: 1px solid #ccc;'>${valor_mensual_solar:.2f}</td>
                </tr>
            </tbody>
        </table>
        """
        st.markdown(html, unsafe_allow_html=True)

    def mostrar_cuadro_inversion(self):
        costos_data_raw = self.session_state.get("costos_data", [])
        costos_data = costos_data_raw.to_dict(orient="records") if isinstance(costos_data_raw, pd.DataFrame) else costos_data_raw

        if not costos_data:
            st.warning("No hay datos disponibles del bloque de inversión.")
            return

        total_inversion = 0.0

        html = ""
        html += "<div style='border:1px solid #ccc; border-radius:10px; padding:15px; margin-top:20px; background-color:#fafafa;'>"
        html += "<h4 style='margin-bottom:20px;'>💰 Inversión</h4>"
        html += "<table style='width:100%; border-collapse:collapse;'>"
        html += "<thead><tr style='background-color:#f0f0f0;'>"
        html += "<th style='text-align:left; padding:8px;'>Detalle</th>"
        html += "<th style='text-align:right; padding:8px;'>Cantidad</th>"
        html += "<th style='text-align:right; padding:8px;'>PVP</th>"
        html += "<th style='text-align:right; padding:8px;'>Total PVP</th>"
        html += "</tr></thead><tbody>"

        for item in costos_data:
            try:
                if isinstance(item, str):
                    continue
                if isinstance(item, dict):
                    detalle = item.get("Detalle", "")
                    cantidad = item.get("Cantidad", 0)
                    pvp = item.get("PVP", 0)
                    total_pvp = item.get("Total PVP", 0)  # Asegúrate que aquí sea el campo correcto
                else:
                    continue

                cantidad_float = float(str(cantidad).replace(",", "")) if cantidad else 0.0
                pvp_float = float(str(pvp).replace(",", "")) if pvp else 0.0
                total_pvp_float = float(str(total_pvp).replace(",", "")) if total_pvp else 0.0

                total_inversion += total_pvp_float

                html += f"<tr><td style='padding:6px 8px;'>{detalle}</td>"
                html += f"<td style='text-align:right; padding:6px 8px;'>{int(cantidad_float)}</td>"
                html += f"<td style='text-align:right; padding:6px 8px;'>${pvp_float:.2f}</td>"
                html += f"<td style='text-align:right; padding:6px 8px;'>${total_pvp_float:.2f}</td></tr>"
            except Exception as e:
                st.error(f"Error procesando item {item}: {str(e)}")
                continue
        html += f"<tr style='background-color:#f0f0f0; font-weight:bold;'>"
        html += f"<td colspan='3' style='text-align:right; padding:8px;'>INVERSIÓN TOTAL</td>"
        html += f"<td style='text-align:right; padding:8px;'>${total_inversion:.2f}</td></tr>"
        html += "</tbody></table></div>"

        st.markdown(html, unsafe_allow_html=True)

    def mostrar_bloque_analisis_economico(self):
        consumo_data = self.session_state.get("consumo_data", {})
        generacion_data = self.session_state.get("generacion_data", {})

        # Obtener los valores desde el bloque "Sistema híbrido"
        costo_mensual = self.convertir_a_float(consumo_data.get("Total A", 0))                       + self.convertir_a_float(consumo_data.get("Total B", 0))                       + self.convertir_a_float(consumo_data.get("Total C", 0))                       + self.convertir_a_float(consumo_data.get("Total D", 0))                       + self.convertir_a_float(consumo_data.get("Total Demanda", 0))

        produccion_kwh_solar = self.convertir_a_float(str(generacion_data.get("kWm", "")).replace("kWh", "").strip())
        kwhA = self.convertir_a_float(consumo_data.get("kW/h A", 0))
        totalA = self.convertir_a_float(consumo_data.get("Total A", 0))
        costo_horario_a = totalA / kwhA if kwhA else 0
        ahorro_solar = round(produccion_kwh_solar * costo_horario_a, 2)

        valor_final = round(costo_mensual - ahorro_solar, 2)

        html = f"""
        <style>
            .tabla-analisis {{
                width: 100%;
                border-collapse: collapse;
                font-size: 16px;
                margin-top: 20px;
            }}
            .tabla-analisis th, .tabla-analisis td {{
                padding: 10px;
                border: 1px solid #ccc;
            }}
            .tabla-analisis th {{
                background-color: #014421;
                color: white;
                text-align: left;
                font-size: 18px;
            }}
            .fila-normal {{
                background-color: #ffffff;
            }}
            .fila-verde {{
                background-color: #ccf2cc;
                font-weight: bold;
            }}
            .fila-final {{
                background-color: #014421;
                color: white;
                font-weight: bold;
            }}
            .right {{
                text-align: right;
            }}
        </style>

        <table class="tabla-analisis">
            <thead>
                <tr>
                    <th colspan="2">Análisis económico</th>
                </tr>
            </thead>
            <tbody>
                <tr class="fila-normal">
                    <td>Costo de electricidad actual (promedio mensual)</td>
                    <td class="right">${costo_mensual:.2f}</td>
                </tr>
                <tr class="fila-verde">
                    <td>Ahorro por energía solar (promedio mensual)</td>
                    <td class="right">${ahorro_solar:.2f}</td>
                </tr>
                <tr class="fila-final">
                    <td>Valor a pagar a la empresa eléctrica</td>
                    <td class="right">${valor_final:.2f}</td>
                </tr>
            </tbody>
        </table>
        """

        st.markdown(html, unsafe_allow_html=True)

    def mostrar_bloque_roi(self):
        # Obtener datos
        costos_data_raw = self.session_state.get("costos_data", [])
        costos_data = costos_data_raw.to_dict(orient="records") if isinstance(costos_data_raw, pd.DataFrame) else costos_data_raw
        total_inversion = 0.0

        for item in costos_data:
            try:
                if isinstance(item, dict):
                    total_pvp = item.get("Total PVP", 0)
                    total_pvp_float = float(str(total_pvp).replace(",", "")) if total_pvp else 0.0
                    total_inversion += total_pvp_float
            except:
                continue

        generacion_data = self.session_state.get("generacion_data", {})
        consumo_data = self.session_state.get("consumo_data", {})
        produccion_kwh_solar = self.convertir_a_float(str(generacion_data.get("kWm", "")).replace("kWh", "").strip())
        totalA = self.convertir_a_float(consumo_data.get("Total A", 0))
        kwhA = self.convertir_a_float(consumo_data.get("kW/h A", 0))
        costo_horario_a = totalA / kwhA if kwhA else 0
        ahorro_mensual = round(produccion_kwh_solar * costo_horario_a, 2)

        # Cálculo ROI
        if ahorro_mensual > 0:
            meses = int(total_inversion // ahorro_mensual)
            anios = meses // 12
            remanente = meses % 12
            retorno_str = f"{anios} Años y {remanente} Meses"
        else:
            retorno_str = "No calculable"

        html = f"""
        <style>
            .tabla-roi {{
                width: 100%;
                border-collapse: collapse;
                font-size: 16px;
                margin-top: 20px;
            }}
            .tabla-roi th, .tabla-roi td {{
                padding: 10px;
                border: 1px solid #ccc;
            }}
            .tabla-roi th {{
                background-color: #014421;
                color: white;
                text-align: left;
                font-size: 18px;
            }}
            .fila-normal {{
                background-color: #ffffff;
            }}
            .fila-verde {{
                background-color: #ccf2cc;
                font-weight: bold;
            }}
            .fila-final {{
                background-color: #014421;
                color: white;
                font-weight: bold;
            }}
            .right {{
                text-align: right;
            }}
        </style>

        <table class="tabla-roi">
            <thead>
                <tr>
                    <th colspan="2">ROI</th>
                </tr>
            </thead>
            <tbody>
                <tr class="fila-normal">
                    <td>Implementación de energía solar (~2%)</td>
                    <td class="right">${total_inversion:.2f}</td>
                </tr>
                <tr class="fila-verde">
                    <td>Ahorro mensual (promedio)</td>
                    <td class="right">${ahorro_mensual:.2f}</td>
                </tr>
                <tr class="fila-final">
                    <td>RETORNO DE INVERSIÓN</td>
                    <td class="right">{retorno_str}</td>
                </tr>
            </tbody>
        </table>
        """

        st.markdown(html, unsafe_allow_html=True)
