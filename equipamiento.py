import pandas as pd
from pathlib import Path
import streamlit as st
import math

class EquipamientoManager:
    def __init__(self, session_state):
        self.session_state = session_state
        self.df_equipamientos = {}
        self.hojas_equipamientos = [
            'Paneles Solares', 'Inversores', 'Baterías', 
            'Convertidor de Alto Voltaje DC', 'Materiales Estructura Solar',
            'Materiales DB'
        ]
        
        self.inicializar_session_state()
        self.cargar_datos()
    
    def inicializar_session_state(self):
        if 'equipamiento_seleccionado' not in self.session_state:
            self.session_state['equipamiento_seleccionado'] = {hoja: None for hoja in self.hojas_equipamientos}
        if 'filtros_equipamiento' not in self.session_state:
            self.session_state['filtros_equipamiento'] = {
                'Paneles Solares': {
                    'Marca': None,
                    'Capacidad': None,
                    'Caras': None,
                    'Modelo': None
                },
                'Inversores': {
                    'Marca': None,
                    'Fases': None,
                    'Tipo': None,
                    'Capacidad': None,
                    'Modelo': None
                },
                'Baterías': {
                    'Marca': None,
                    'Tipo': None,
                    'Capacidad': None,
                    'Modelo': None
                },
                'Convertidor de Alto Voltaje DC': {
                    'Marca': None,
                    'Tipo': None,
                    'Voltaje': None,
                    'Modelo': None
                },
                'Materiales Estructura Solar': {
                    'Tipo': None,
                    'Material': None,
                    'Modelo': None
                }
            }


        if 'materiales_seleccionados' not in self.session_state:
             self.session_state.materiales_seleccionados = []


    def cargar_datos(self):
        try:
            desktop_path = Path.home() / 'Desktop'
            folder_path = desktop_path / 'Calculadora_Solar'
            calc_path = folder_path / 'Calculadora Solar.xlsx'
            if calc_path.exists():
                excel_file = pd.ExcelFile(calc_path)
                hojas_existentes = excel_file.sheet_names
                for hoja in self.hojas_equipamientos:
                    if hoja in hojas_existentes:
                        try:
                            df = pd.read_excel(calc_path, sheet_name=hoja)
                            if not df.empty:
                                df.columns = [col.strip() for col in df.columns]
                                if 'Marca' in df.columns and 'Modelo' in df.columns:
                                    df['nombre_display'] = df['Marca'] + " " + df['Modelo']
                                else:
                                    nombre_col = next((col for col in df.columns if 'nombre' in col.lower() or 'modelo' in col.lower() or 'tipo' in col.lower()), df.columns[0])
                                    df['nombre_display'] = df[nombre_col].astype(str)
                                df = df.dropna(how='all').fillna("")
                                if hoja == 'Paneles Solares' and 'Caras' not in df.columns:
                                    df['Caras'] = '1'
                                if hoja == 'Inversores' and 'Tipo' not in df.columns:
                                    df['Tipo'] = 'No especificado'
                                self.df_equipamientos[hoja] = df
                            else:
                                self.df_equipamientos[hoja] = pd.DataFrame()
                        except Exception as e:
                            st.error(f"Error al cargar hoja {hoja}: {str(e)}")
                            self.df_equipamientos[hoja] = pd.DataFrame()
                    else:
                        self.df_equipamientos[hoja] = pd.DataFrame()
                        st.warning(f"Hoja '{hoja}' no encontrada en el archivo Excel. Se creará un DataFrame vacío.")
        except Exception as e:
            st.error(f"Error general: {str(e)}")
    
    def formatear_decimal(self, valor, decimales=2):
        try:
            valor = float(valor)
            return f"{valor:.{decimales}f}"
        except:
            return f"0.{'0'*decimales}"
    
    def formatear_pvp(self, valor):
        try:
            valor = float(valor)
            return f"{valor:.2f}"
        except:
            return "0.00"
    
    def mostrar_pestana(self):
        st.header("⚙️ Equipamientos")
        
        for hoja in self.hojas_equipamientos:
            with st.expander(hoja):
                self.mostrar_equipamiento(hoja)
    
    def mostrar_equipamiento(self, hoja):
        if hoja not in self.df_equipamientos or self.df_equipamientos[hoja].empty:
            st.warning(f"No hay datos disponibles para {hoja}")
            return
        df = self.df_equipamientos[hoja]
        if st.button(f"➕ Ingresar nuevo {hoja.split()[0].lower()}", key=f"btn_nuevo_{hoja}"):
            st.session_state[f'nuevo_{hoja.lower()}'] = True
            st.info(f"Funcionalidad para agregar nuevo {hoja} en desarrollo")
        st.markdown("---")
        if hoja == 'Materiales Estructura Solar':
            self.mostrar_filtros_estructura_solar(df)
        else:
            self.mostrar_filtros_generico(df, hoja)


    def mostrar_filtros_generico(self, df, hoja):
        columnas = ['Marca', 'Tipo', 'Capacidad', 'Modelo', 'Fases', 'Caras', 'Voltaje']
        df_filtrado = df.copy()
    
        # Aplicar filtros
        for col in columnas:
            if col in df.columns:
                # Si la columna es 'Capacidad', forzamos a enteros como string
                if col == 'Capacidad':
                    opciones_raw = pd.to_numeric(df[col], errors='coerce').dropna()
                    opciones = sorted(list(set([str(int(c)) for c in opciones_raw])))
                    seleccion = st.selectbox(col, ["Todos"] + opciones, index=0, key=f"{hoja}_{col}")
                    if seleccion != "Todos":
                        df_filtrado = df_filtrado[df_filtrado[col].apply(lambda x: str(int(float(x))) if str(x).replace('.', '', 1).isdigit() else "") == seleccion]
                else:
                    opciones = sorted(df[col].dropna().astype(str).unique().tolist())
                    seleccion = st.selectbox(col, ["Todos"] + opciones, index=0, key=f"{hoja}_{col}")
                    if seleccion != "Todos":
                        df_filtrado = df_filtrado[df_filtrado[col].astype(str) == seleccion]
    
        if df_filtrado.empty:
            st.warning("No hay equipos que coincidan con los filtros seleccionados")
            return
    
        nombres = df_filtrado['nombre_display'].unique().tolist()
        seleccion_previa = self.session_state['equipamiento_seleccionado'].get(hoja)
    
        try:
            index_previo = nombres.index(seleccion_previa) if seleccion_previa in nombres else 0
        except:
            index_previo = 0
    
        seleccionado = st.selectbox(f"Seleccione un equipo de {hoja}", nombres, index=index_previo, key=f"{hoja}_selector")
    
        if seleccionado:
            equipo_data = df_filtrado[df_filtrado['nombre_display'] == seleccionado].iloc[0].to_dict()
            self.session_state['equipamiento_seleccionado'][hoja] = seleccionado
        
            # Mostrar detalles del equipo seleccionado
            if hoja == 'Paneles Solares':
                self.mostrar_detalles_panel(equipo_data)
                self.session_state['distribucion_data']['panel_seleccionado'] = seleccionado
                self.session_state['distribucion_data']['distribucion_actualizada'] = False
            elif hoja == 'Inversores':
                self.mostrar_detalles_inversor(equipo_data)
            elif hoja == 'Baterías':
                self.mostrar_detalles_bateria(equipo_data)
            elif hoja == 'Convertidor de Alto Voltaje DC':
                self.mostrar_detalles_convertidor(equipo_data)
            elif hoja == 'Materiales Estructura Solar':
                self.mostrar_detalles_estructura_solar(equipo_data)
            else:
                self.mostrar_detalles_equipo(hoja, equipo_data)

    def mostrar_filtros_paneles(self, df):
        marcas = sorted(df['Marca'].unique().tolist()) if 'Marca' in df.columns else []
        
        marca_seleccionada = st.selectbox(
            "Marca",
            options=["Todas"] + marcas,
            index=0,
            key="filtro_marca_panel"
        )
        
        df_filtrado = df.copy()
        if marca_seleccionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Marca'] == marca_seleccionada]
        
        capacidades = []
        if 'Capacidad' in df_filtrado.columns:
            try:
                capacidades = (
                    pd.to_numeric(df_filtrado['Capacidad'], errors='coerce')
                    .dropna()
                    .apply(lambda x: str(int(round(x))))
                    .unique()
                    .tolist()
                )
                capacidades = sorted(capacidades, key=lambda x: int(x))
            except:
                capacidades = sorted(list(set([str(int(float(c))) for c in df_filtrado['Capacidad'] if pd.notnull(c)])))
        
        capacidad_seleccionada = st.selectbox(
            "Capacidad (W)",
            options=["Todas"] + capacidades,
            index=0,
            key="filtro_capacidad_panel"
        )
        
        if capacidad_seleccionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Capacidad'].apply(lambda x: str(int(round(float(x)))) if pd.notnull(x) else '') == capacidad_seleccionada]
        
        caras = sorted(df_filtrado['Caras'].unique().tolist()) if 'Caras' in df_filtrado.columns else []
        
        caras_seleccionadas = st.selectbox(
            "Caras",
            options=["Todas"] + caras,
            index=0,
            key="filtro_caras_panel"
        )
        
        if caras_seleccionadas != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Caras'] == caras_seleccionadas]
        
        modelos = sorted(df_filtrado['Modelo'].unique().tolist()) if 'Modelo' in df_filtrado.columns else []
        
        modelo_seleccionado = st.selectbox(
            "Modelo",
            options=["Todos"] + modelos,
            index=0,
            key="filtro_modelo_panel"
        )
        
        if modelo_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Modelo'] == modelo_seleccionado]
        
        if df_filtrado.empty:
            st.warning("No hay paneles que coincidan con los filtros seleccionados")
            return
        
        nombres_paneles = df_filtrado['nombre_display'].unique().tolist()
        panel_seleccionado = st.selectbox(
            "Seleccione un panel solar",
            options=nombres_paneles,
            index=0,
            key="selector_panel_solar"
        )
        
        if panel_seleccionado:
            panel_data = df_filtrado[df_filtrado['nombre_display'] == panel_seleccionado].iloc[0].to_dict()
            self.mostrar_detalles_panel(panel_data)
            
            nombre_panel = f"{panel_data.get('Marca', '')} {panel_data.get('Modelo', '')}"
            if self.session_state['equipamiento_seleccionado']['Paneles Solares'] != nombre_panel:
                self.session_state['equipamiento_seleccionado']['Paneles Solares'] = nombre_panel
                self.session_state['distribucion_data']['panel_seleccionado'] = nombre_panel
                self.session_state['distribucion_data']['distribucion_actualizada'] = False
                st.rerun()
    
    def mostrar_filtros_inversores(self, df):
        marcas = sorted(df['Marca'].unique().tolist()) if 'Marca' in df.columns else []
        
        marca_seleccionada = st.selectbox(
            "Marca",
            options=["Todas"] + marcas,
            index=0,
            key="filtro_marca_inversor"
        )
        
        df_filtrado = df.copy()
        if marca_seleccionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Marca'] == marca_seleccionada]
        
        fases = []
        if 'Fases' in df_filtrado.columns:
            try:
                fases = df_filtrado['Fases'].astype(str).dropna().unique().tolist()
                fases = sorted([f for f in fases if f.strip()])
            except Exception as e:
                st.error(f"Error al procesar fases: {str(e)}")
                fases = []
        
        fases_seleccionadas = st.selectbox(
            "Fases",
            options=["Todas"] + fases,
            index=0,
            key="filtro_fases_inversor"
        )
        
        if fases_seleccionadas != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Fases'].astype(str) == fases_seleccionadas]
        
        tipos = []
        if 'Tipo' in df_filtrado.columns:
            try:
                tipos = df_filtrado['Tipo'].astype(str).dropna().unique().tolist()
                tipos = sorted([t for t in tipos if t.strip()])
            except:
                tipos = []
        
        tipo_seleccionado = st.selectbox(
            "Tipo",
            options=["Todos"] + tipos,
            index=0,
            key="filtro_tipo_inversor"
        )
        
        if tipo_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_seleccionado]
        
        capacidades_raw = pd.to_numeric(df_filtrado['Capacidad'], errors='coerce').dropna()
        capacidades_enteras = sorted(list(set([str(int(c)) for c in capacidades_raw])))

        capacidad_seleccionada = st.selectbox(
            "Capacidad (W)",
            options=["Todas"] + capacidades_enteras,
            index=0,
            key="filtro_capacidad_panel"
        )

        if capacidad_seleccionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Capacidad'].apply(lambda x: str(int(float(x))) if pd.notnull(x) else "") == capacidad_seleccionada]
        
        modelos = []
        if 'Modelo' in df_filtrado.columns:
            try:
                modelos = df_filtrado['Modelo'].astype(str).dropna().unique().tolist()
                modelos = sorted([m for m in modelos if m.strip()])
            except:
                modelos = []
        
        modelo_seleccionado = st.selectbox(
            "Modelo",
            options=["Todos"] + modelos,
            index=0,
            key="filtro_modelo_inversor"
        )
        
        if modelo_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Modelo'] == modelo_seleccionado]
        
        if df_filtrado.empty:
            st.warning("No hay inversores que coincidan con los filtros seleccionados")
            return
        
        nombres_inversores = df_filtrado['nombre_display'].unique().tolist()
        inversor_seleccionado = st.selectbox(
            "Seleccione un inversor",
            options=nombres_inversores,
            index=0,
            key="selector_inversor"
        )
        
        if inversor_seleccionado:
            inversor_data = df_filtrado[df_filtrado['nombre_display'] == inversor_seleccionado].iloc[0].to_dict()
            self.mostrar_detalles_inversor(inversor_data)
            
            nombre_inversor = f"{inversor_data.get('Marca', '')} {inversor_data.get('Modelo', '')}"
            if self.session_state['equipamiento_seleccionado']['Inversores'] != nombre_inversor:
                self.session_state['equipamiento_seleccionado']['Inversores'] = nombre_inversor
                st.rerun()
    
    def mostrar_filtros_baterias(self, df):
        marcas = sorted(df['Marca'].unique().tolist()) if 'Marca' in df.columns else []
        
        marca_seleccionada = st.selectbox(
            "Marca",
            options=["Todas"] + marcas,
            index=0,
            key="filtro_marca_bateria"
        )
        
        df_filtrado = df.copy()
        if marca_seleccionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Marca'] == marca_seleccionada]
        
        tipos = []
        if 'Tipo' in df_filtrado.columns:
            try:
                tipos = df_filtrado['Tipo'].astype(str).dropna().unique().tolist()
                tipos = sorted([t for t in tipos if t.strip()])
            except:
                tipos = []
        
        tipo_seleccionado = st.selectbox(
            "Tipo",
            options=["Todos"] + tipos,
            index=0,
            key="filtro_tipo_bateria"
        )
        
        if tipo_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_seleccionado]
        
        capacidades_raw = pd.to_numeric(df_filtrado['Capacidad'], errors='coerce').dropna()
        capacidades_enteras = sorted(list(set([str(int(c)) for c in capacidades_raw])))

        capacidad_seleccionada = st.selectbox(
            "Capacidad (KW)",
            options=["Todas"] + capacidades_enteras,
            index=0,
            key="filtro_capacidad_panel"
        )

        if capacidad_seleccionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Capacidad'].apply(lambda x: str(int(float(x))) if pd.notnull(x) else "") == capacidad_seleccionada]
        
        modelos = []
        if 'Modelo' in df_filtrado.columns:
            try:
                modelos = df_filtrado['Modelo'].astype(str).dropna().unique().tolist()
                modelos = sorted([m for m in modelos if m.strip()])
            except:
                modelos = []
        
        modelo_seleccionado = st.selectbox(
            "Modelo",
            options=["Todos"] + modelos,
            index=0,
            key="filtro_modelo_bateria"
        )
        
        if modelo_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Modelo'] == modelo_seleccionado]
        
        if df_filtrado.empty:
            st.warning("No hay baterías que coincidan con los filtros seleccionados")
            return
        
        nombres_baterias = df_filtrado['nombre_display'].unique().tolist()
        bateria_seleccionada = st.selectbox(
            "Seleccione una batería",
            options=nombres_baterias,
            index=0,
            key="selector_bateria"
        )
        
        if bateria_seleccionada:
            bateria_data = df_filtrado[df_filtrado['nombre_display'] == bateria_seleccionada].iloc[0].to_dict()
            self.mostrar_detalles_bateria(bateria_data)
            
            nombre_bateria = f"{bateria_data.get('Marca', '')} {bateria_data.get('Modelo', '')}"
            if self.session_state['equipamiento_seleccionado']['Baterías'] != nombre_bateria:
                self.session_state['equipamiento_seleccionado']['Baterías'] = nombre_bateria
                st.rerun()
    
    def mostrar_filtros_convertidores(self, df):
        marcas = sorted(df['Marca'].unique().tolist()) if 'Marca' in df.columns else []
        
        marca_seleccionada = st.selectbox(
            "Marca",
            options=["Todas"] + marcas,
            index=0,
            key="filtro_marca_convertidor"
        )
        
        df_filtrado = df.copy()
        if marca_seleccionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Marca'] == marca_seleccionada]
        
        tipos = []
        if 'Tipo' in df_filtrado.columns:
            try:
                tipos = df_filtrado['Tipo'].astype(str).dropna().unique().tolist()
                tipos = sorted([t for t in tipos if t.strip()])
            except:
                tipos = []
        
        tipo_seleccionado = st.selectbox(
            "Tipo",
            options=["Todos"] + tipos,
            index=0,
            key="filtro_tipo_convertidor"
        )
        
        if tipo_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_seleccionado]
        
        voltajes = []
        if 'Voltaje' in df_filtrado.columns:
            try:
                voltajes = pd.to_numeric(df_filtrado['Voltaje'], errors='coerce').dropna().unique()
                voltajes = sorted(voltajes.tolist())
            except:
                voltajes = sorted(df_filtrado['Voltaje'].astype(str).unique().tolist())
        
        voltaje_seleccionado = st.selectbox(
            "Voltaje (V)",
            options=["Todos"] + voltajes,
            index=0,
            key="filtro_voltaje_convertidor"
        )
        
        if voltaje_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Voltaje'].astype(str) == str(voltaje_seleccionado)]
        
        modelos = []
        if 'Modelo' in df_filtrado.columns:
            try:
                modelos = df_filtrado['Modelo'].astype(str).dropna().unique().tolist()
                modelos = sorted([m for m in modelos if m.strip()])
            except:
                modelos = []
        
        modelo_seleccionado = st.selectbox(
            "Modelo",
            options=["Todos"] + modelos,
            index=0,
            key="filtro_modelo_convertidor"
        )
        
        if modelo_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Modelo'] == modelo_seleccionado]
        
        if df_filtrado.empty:
            st.warning("No hay convertidores que coincidan con los filtros seleccionados")
            return
        
        nombres_convertidores = df_filtrado['nombre_display'].unique().tolist()
        convertidor_seleccionado = st.selectbox(
            "Seleccione un convertidor",
            options=nombres_convertidores,
            index=0,
            key="selector_convertidor"
        )
        
        if convertidor_seleccionado:
            convertidor_data = df_filtrado[df_filtrado['nombre_display'] == convertidor_seleccionado].iloc[0].to_dict()
            self.mostrar_detalles_convertidor(convertidor_data)
            
            nombre_convertidor = f"{convertidor_data.get('Marca', '')} {convertidor_data.get('Modelo', '')}"
            if self.session_state['equipamiento_seleccionado']['Convertidor de Alto Voltaje DC'] != nombre_convertidor:
                self.session_state['equipamiento_seleccionado']['Convertidor de Alto Voltaje DC'] = nombre_convertidor
                st.rerun()
    
    def mostrar_filtros_estructura_solar(self, df):
        if df.empty:
            st.warning("No hay datos disponibles para materiales de estructura solar")
            return

        if 'Descripción' not in df.columns:
            st.error("La columna 'Descripción' no existe en la hoja de materiales")
            return

        # Obtener lista única de descripciones
        descripciones = sorted(df['Descripción'].dropna().unique().tolist())

        # Inicializar lista de selecciones en session_state si no existe
        if 'materiales_seleccionados' not in self.session_state:
            self.session_state.materiales_seleccionados = []

        # Crear 5 dropdowns verticales sin labels
        st.markdown("#### Seleccione materiales:")

        selecciones_actuales = []

        # Dropdown 1
        seleccion_1 = st.selectbox(
            "",
            options=[""] + descripciones,
            key="dropdown_1_estructura",
            label_visibility="collapsed"
        )
        if seleccion_1:
            selecciones_actuales.append(seleccion_1)

        # Dropdown 2
        seleccion_2 = st.selectbox(
            "",
            options=[""] + descripciones,
            key="dropdown_2_estructura",
            label_visibility="collapsed"
        )
        if seleccion_2:
            selecciones_actuales.append(seleccion_2)

        # Dropdown 3
        seleccion_3 = st.selectbox(
            "",
            options=[""] + descripciones,
            key="dropdown_3_estructura",
            label_visibility="collapsed"
        )
        if seleccion_3:
            selecciones_actuales.append(seleccion_3)

        # Dropdown 4
        seleccion_4 = st.selectbox(
            "",
            options=[""] + descripciones,
            key="dropdown_4_estructura",
            label_visibility="collapsed"
        )
        if seleccion_4:
            selecciones_actuales.append(seleccion_4)

        # Dropdown 5
        seleccion_5 = st.selectbox(
            "",
            options=[""] + descripciones,
            key="dropdown_5_estructura",
            label_visibility="collapsed"
        )
        if seleccion_5:
            selecciones_actuales.append(seleccion_5)

        # Actualizar lista de selecciones (eliminar duplicados y vacíos)
        selecciones_unicas = list(set([s for s in selecciones_actuales if s]))

        # Mostrar cuadro con materiales seleccionados
        if selecciones_unicas:
            st.markdown("---")
            st.subheader("Materiales seleccionados")
    
            # Filtrar DataFrame con los seleccionados
            df_seleccionados = df[df['Descripción'].isin(selecciones_unicas)]
    
            # Configurar columnas a mostrar
            columnas_mostrar = ['Descripción']
            if 'PVP' in df.columns:
                columnas_mostrar.append('PVP')
                # Calcular total
                total = df_seleccionados['PVP'].sum()
    
            # Mostrar tabla con estilo profesional
            st.dataframe(
                df_seleccionados[columnas_mostrar],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Descripción": "Material",
                    "PVP": st.column_config.NumberColumn(
                        "Precio",
                        format="$%.2f"
                    )
                }
            )
    
            # Mostrar total si existe PVP
            if 'PVP' in df.columns:
                st.markdown(f"**Total:** ${total:,.2f}")

        # --- NUEVO CÓDIGO PARA MOSTRAR EL CUADRO DE CLAMPS DINÁMICO ---
        st.markdown("---")
        st.subheader("Especificaciones de Clamps")

        # Inicializar medidas con "No seleccionado"
        clamp_medidas = {
            "End Clamp": "No seleccionado",
            "Mid Clamp": "No seleccionado",
            "L Foot": "No seleccionado",
            "Roof Clamp": "No seleccionado"
        }

        # Buscar medidas en los materiales seleccionados
        if 'materiales_seleccionados' in self.session_state:
            for material in self.session_state.materiales_seleccionados:
                material_data = df[df['Descripción'].str.strip().str.lower() == material.strip().lower()]
        
                if not material_data.empty and 'Tomar en cuenta' in material_data.columns:
                    medida = material_data['Tomar en cuenta'].values[0]
            
                    # Detección robusta del tipo de clamp (insensible a mayúsculas/espacios)
                    if 'end' in material.lower() and 'clamp' in material.lower():
                        clamp_medidas["End Clamp"] = medida
                    elif 'mid' in material.lower() and 'clamp' in material.lower():
                        clamp_medidas["Mid Clamp"] = medida
                    elif 'l foot' in material.lower() or 'l-foot' in material.lower():
                        clamp_medidas["L Foot"] = medida
                    elif 'roof' in material.lower() and 'clamp' in material.lower():
                        clamp_medidas["Roof Clamp"] = medida

        # Crear y mostrar el DataFrame
        df_clamps = pd.DataFrame({
            "Clamps": list(clamp_medidas.keys()),
            "Medida": list(clamp_medidas.values())
        })

        st.dataframe(
            df_clamps,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Clamps": "Tipo de Clamp",
                "Medida": st.column_config.TextColumn(
                    "Medida",
                    help="Valor de la columna 'Tomar en cuenta'"
                )
            }
        )
    
        # Nota explicativa
        st.caption("Las medidas se actualizan automáticamente al seleccionar los materiales correspondientes.")
        # --- FIN DEL NUEVO CÓDIGO ---

        # Guardar selecciones en session state
        self.session_state.materiales_seleccionados = selecciones_unicas
    
    def mostrar_detalles_panel(self, panel_data):
        st.subheader(f"{panel_data.get('Marca', '')} {panel_data.get('Modelo', '')}")
        
        try:
            voc_original = float(panel_data.get('VOC', 0))
            voc_ajustado = voc_original * 1.028
        except:
            voc_original = 0
            voc_ajustado = 0
        
        st.markdown("""<style>...</style>""", unsafe_allow_html=True)  # omito estilo por brevedad
        
        st.markdown(f"""
        <table class="panel-table">
            <tr><th>Dimensiones de Panel</th><th>Especificación</th><th>Medidas</th></tr>
            <tr><td>Largo</td><td>Media Portal (Y)</td><td>{panel_data.get('Alto', '')} M</td></tr>
            <tr><td>Ancho</td><td>Media Landscape (X)</td><td>{panel_data.get('Ancho', '')} M</td></tr>
            <tr><td>Espesor</td><td>Espesor del panel</td><td>{panel_data.get('Espesor', '0.000')} M</td></tr>
            <tr><td>Área</td><td>(Largo X Ancho)</td><td>{self.formatear_decimal(panel_data.get('Metros²', ''), 3)} M²</td></tr>
            <tr><td>Watts</td><td>Capacidad Nominal del panel</td><td>{int(float(panel_data.get('Capacidad', 0)))} W</td></tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"**Capacidad:** {int(float(panel_data.get('Capacidad', 0)))} W")
            st.markdown(f"**NOCT:** {math.ceil(float(panel_data.get('NOCT', 0)))}")
        with cols[1]:
            st.markdown(f"**VOC:** {self.formatear_decimal(voc_ajustado)}")
            st.markdown(f"**Cells:** {self.formatear_decimal(panel_data.get('Cells', ''))}")
        
        st.markdown(f"**PVP:** ${self.formatear_pvp(panel_data.get('PVP', ''))}")

    def mostrar_detalles_inversor(self, inversor_data):
        st.subheader(f"{inversor_data.get('Marca', '')} {inversor_data.get('Modelo', '')}")
        
        panel_seleccionado = self.session_state['equipamiento_seleccionado'].get('Paneles Solares')
        voc_panel = 0
        max_panels_per_string = "N/A"
        max_panel_per_inverter = "N/A"
        
        if panel_seleccionado and 'Paneles Solares' in self.df_equipamientos:
            try:
                panel_df = self.df_equipamientos['Paneles Solares']
                panel_data = panel_df[panel_df['nombre_display'] == panel_seleccionado].iloc[0].to_dict()
                voc_original = float(panel_data.get('VOC', 0))
                voc_panel = voc_original * 1.028
            except:
                voc_panel = 0
        
        try:
            max_pv_input_voltage = float(inversor_data.get('Max PV Input Voltage', 0))
            strings = float(inversor_data.get('Strings', 0))
            if voc_panel > 0 and max_pv_input_voltage > 0 and strings > 0:
                max_panels_per_string = max_pv_input_voltage / voc_panel
                max_panels_per_string_rounded = int(max_panels_per_string)
                max_panel_per_inverter = max_panels_per_string_rounded * int(strings)
        except:
            max_panels_per_string_rounded = "N/A"
            max_panel_per_inverter = "N/A"
        
        tipo_inversor = inversor_data.get('Tipo', 'No especificado')
        if 'híbrido' in tipo_inversor.lower() or 'hibrido' in tipo_inversor.lower():
            tipo_inversor = "Híbrido"
        elif 'string' in tipo_inversor.lower():
            tipo_inversor = "String"
        
        st.markdown("""<style>...</style>""", unsafe_allow_html=True)  # omito estilo por brevedad

        st.markdown(f"""
        <table class="inversor-table">
            <tr><th>Especificación</th><th>Valor</th></tr>
            <tr><td>Tipo</td><td>{tipo_inversor}</td></tr>
            <tr><td>Capacidad</td><td>{self.formatear_decimal(inversor_data.get('Capacidad', ''))} kW</td></tr>
            <tr><td>Fases</td><td>{inversor_data.get('Fases', '')}</td></tr>
            <tr><td>Voltage AC</td><td>{inversor_data.get('Voltage AC', '')}</td></tr>
            <tr><td>Max PV Input Voltage</td><td>{int(float(inversor_data.get('Max PV Input Voltage', 0)))} V</td></tr>
            <tr><td>Max PV Acess Power</td><td>{int(float(inversor_data.get('Max PV Acess Power', 0)))} W</td></tr>
            <tr><td>MPPT</td><td>{int(float(inversor_data.get('MPPT', 0)))}</td></tr>
            <tr><td>Strings</td><td>{int(float(inversor_data.get('Strings', 0)))}</td></tr>
            <tr><td>Max Panels per string</td><td>{max_panels_per_string_rounded}</td></tr>
            <tr><td>Max Panel per Inverter</td><td>{max_panel_per_inverter}</td></tr>
            <tr><td>Battery Voltage</td><td>{inversor_data.get('Battery Voltage', '')}</td></tr>
        </table>
        """, unsafe_allow_html=True)
        
        if not panel_seleccionado:
            st.warning("⚠️ Para calcular 'Max Panels per string' y 'Max Panel per Inverter', primero seleccione un panel solar")
        
        st.markdown(f"**PVP:** ${self.formatear_pvp(inversor_data.get('PVP', ''))}")
    
    def mostrar_detalles_bateria(self, bateria_data):
        st.subheader(f"{bateria_data.get('Marca', '')} {bateria_data.get('Modelo', '')}")
        
        st.markdown("""
        <style>
        .bateria-table {
            width: 100%;
            border-collapse: collapse;
        }
        .bateria-table th, .bateria-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .bateria-table th {
            background-color: #f2f2f2;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <table class="bateria-table">
            <tr>
                <th>Especificación</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Tipo</td>
                <td>{bateria_data.get('Tipo', '')}</td>
            </tr>
            <tr>
                <td>Capacidad</td>
                <td>{self.formatear_decimal(bateria_data.get('Capacidad', ''))} kWh</td>
            </tr>
            <tr>
                <td>Voltaje</td>
                <td>{self.formatear_decimal(bateria_data.get('Voltaje', ''))} V</td>
            </tr>
            <tr>
                <td>Ciclos</td>
                <td>{bateria_data.get('Ciclos', '')}</td>
            </tr>
            <tr>
                <td>Vida Útil</td>
                <td>{bateria_data.get('Vida Útil', '')}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**PVP:** ${self.formatear_pvp(bateria_data.get('PVP', ''))}")
    
    def mostrar_detalles_convertidor(self, convertidor_data):
        st.subheader(f"{convertidor_data.get('Marca', '')} {convertidor_data.get('Modelo', '')}")
        
        st.markdown("""
        <style>
        .convertidor-table {
            width: 100%;
            border-collapse: collapse;
        }
        .convertidor-table th, .convertidor-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .convertidor-table th {
            background-color: #f2f2f2;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <table class="convertidor-table">
            <tr>
                <th>Especificación</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Tipo</td>
                <td>{convertidor_data.get('Tipo', '')}</td>
            </tr>
            <tr>
                <td>Voltaje</td>
                <td>{self.formatear_decimal(convertidor_data.get('Voltaje', ''))} V</td>
            </tr>
            <tr>
                <td>Amperaje</td>
                <td>{self.formatear_decimal(convertidor_data.get('Amperaje', ''))} A</td>
            </tr>
            <tr>
                <td>Eficiencia</td>
                <td>{convertidor_data.get('Eficiencia', '')}</td>
            </tr>
            <tr>
                <td>Rango de Operación</td>
                <td>{convertidor_data.get('Rango de Operación', '')}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**PVP:** ${self.formatear_pvp(convertidor_data.get('PVP', ''))}")
    
    def mostrar_detalles_estructura_solar(self, estructura_data):
        st.subheader(f"{estructura_data.get('Tipo', '')} {estructura_data.get('Modelo', '')}")
        
        st.markdown("""
        <style>
        .estructura-table {
            width: 100%;
            border-collapse: collapse;
        }
        .estructura-table th, .estructura-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .estructura-table th {
            background-color: #f2f2f2;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <table class="estructura-table">
            <tr>
                <th>Especificación</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Tipo</td>
                <td>{estructura_data.get('Tipo', '')}</td>
            </tr>
            <tr>
                <td>Material</td>
                <td>{estructura_data.get('Material', '')}</td>
            </tr>
            <tr>
                <td>Capacidad de Carga</td>
                <td>{self.formatear_decimal(estructura_data.get('Capacidad de Carga', ''))} kg</td>
            </tr>
            <tr>
                <td>Resistencia a Viento</td>
                <td>{estructura_data.get('Resistencia a Viento', '')}</td>
            </tr>
            <tr>
                <td>Garantía</td>
                <td>{estructura_data.get('Garantía', '')}</td>
            </tr>
            <tr>
                <td>Compatible con</td>
                <td>{estructura_data.get('Compatible con', '')}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**PVP:** ${self.formatear_pvp(estructura_data.get('PVP', ''))}")
    
    def mostrar_detalles_equipo(self, hoja, equipo_data):
        st.subheader(equipo_data.get('nombre_display', ''))
    
        # Filtrar columnas que no queremos mostrar
        columnas_ocultas = ['nombre_display', 'PVP']
        especificaciones = {k: v for k, v in equipo_data.items() if k not in columnas_ocultas}
    
        # Mostrar tabla con estilo profesional
        st.markdown("""
        <style>
        .equipo-table {
            width: 100%;
            border-collapse: collapse;
        }
        .equipo-table th, .equipo-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .equipo-table th {
            background-color: #f2f2f2;
        }
        </style>
        """, unsafe_allow_html=True)
    
        st.markdown("<table class='equipo-table'>", unsafe_allow_html=True)
        st.markdown("<tr><th>Especificación</th><th>Valor</th></tr>", unsafe_allow_html=True)
    
        for key, value in especificaciones.items():
            # Formatear valores numéricos
            if isinstance(value, (int, float)):
                if 'Capacidad' in key or 'Voltaje' in key or 'Amperaje' in key:
                    value = f"{value:,.2f}"
                elif 'PVP' in key or 'Precio' in key:
                    value = f"${value:,.2f}"
        
            st.markdown(f"<tr><td>{key}</td><td>{value}</td></tr>", unsafe_allow_html=True)
    
        st.markdown("</table>", unsafe_allow_html=True)
    
        if 'PVP' in equipo_data:
            st.markdown(f"**PVP:** ${self.formatear_pvp(equipo_data['PVP'])}")