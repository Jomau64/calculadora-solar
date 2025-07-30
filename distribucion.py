import pandas as pd
import streamlit as st
from pathlib import Path 
import math
class DistribucionManager:
    def __init__(self, cliente_manager, equipamiento_manager, session_state):
        self.cliente_manager = cliente_manager
        self.equipamiento_manager = equipamiento_manager
        self.session_state = session_state
        self.df_distribucion = pd.DataFrame()
        self.inicializar_session_state()
        self.cargar_datos()

    def inicializar_session_state(self):
        if 'distribucion_data' not in self.session_state:
            self.session_state.distribucion_data = {
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
                    'espacio_bordes': '1 Metros',
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
        else:
            # Asegurar que layout_data siempre exista, incluso si fue cargado desde Excel
            if 'layout_data' not in self.session_state.distribucion_data:
                self.session_state.distribucion_data['layout_data'] = {
                    'orientacion': 'Portrait',
                    'azimuth': '',
                    'pitch': '',
                    'ground_clearence': '',
                    'espacio_bordes': '',
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


    

    def render_orientacion_selector(self, array_index, orientacion_actual):
        return st.selectbox(
            label="",
            options=["Portrait", "Landscape"],
            index=0 if orientacion_actual == "Portrait" else 1,
            key=f"orientacion_array_{array_index+1}"
        )

    def render_orientacion_html(self, array_index):
        selected = self.session_state.get(f"orientacion_array_{array_index+1}", "Portrait")
        return selected
    def cargar_datos(self):
        try:
            desktop_path = Path.home() / 'Desktop'
            folder_path = desktop_path / 'Calculadora_Solar'
            calc_path = folder_path / 'Calculadora Solar.xlsx'
            if calc_path.exists():
                try:
                    self.df_distribucion = pd.read_excel(calc_path, sheet_name='Distribución Solar')
                except ValueError as e:
                    if "Worksheet" in str(e) and "not found" in str(e):
                        st.warning("⚠️ La hoja 'Distribución Solar' no existe. Se creará una hoja vacía.")
                        self.df_distribucion = pd.DataFrame(columns=[
                            "Empresa", "orientacion", "largo_fila", "filas_x_columna", "columnas",
                            "paneles_por_fila", "total_paneles", "total_filas_array", "medida_x", "medida_y"
                        ])
                    else:
                        raise
                except ValueError as e:
                    if "Worksheet" in str(e) and "not found" in str(e):
                        st.warning("⚠️ La hoja 'Distribución Solar' no existe. Se creará una hoja vacía.")
                        self.df_distribucion = pd.DataFrame(columns=[
                            "Empresa", "orientacion", "largo_fila", "filas_x_columna", "columnas",
                            "paneles_por_fila", "total_paneles", "total_filas_array", "medida_x", "medida_y"
                        ])
                    else:
                        raise
                if not self.df_distribucion.empty:
                    self.df_distribucion.columns = [col.strip() for col in self.df_distribucion.columns]
        except Exception as e:
            st.error(f"Error al cargar distribución: {str(e)}")

    def formatear_decimal(self, valor, decimales=2):
        try:
            valor = float(valor)
            return str(int(valor)) if valor.is_integer() else f"{valor:.{decimales}f}"
        except:
            return "0" if decimales == 0 else f"0.{'0'*decimales}"

    def redondear_especial(self, valor):
        try:
            valor = float(valor)
            entero = int(valor)
            decimal = valor - entero
            if decimal >= 0.5:
                return entero + 1
            return entero
        except:
            return 0
    
    def calcular_distribucion_paneles(self, panel_data, array_x, array_y, orientacion):
        import math

        def to_float(val):
            try:
                if isinstance(val, str):
                    val = val.replace(',', '.').strip()
                return float(val) if val else 0.0
            except:
                return 0.0

        default_result = {
            'paneles_fila': "0 Paneles",
            'paneles_columna': "0 Paneles",
            'paneles_array': "0 Paneles",
            'largo_fila': "0.00 Metros",
            'separacion_columnas': "0.00 Metros",
            'separacion_filas': "0.00 Metros",
            'filas_x_columna': "0",
            'columnas': "0",
            'total_filas_array': "0",
            'espacio_utilizado': '0.00m',
            'espacio_bordes': '1.00m cada lado',
            'diseno': "Configuración no válida"
        }

        try:
            medida_X = to_float(array_x)
            medida_Y = to_float(array_y)
            largo_panel = to_float(panel_data.get('Alto', 0))
            ancho_panel = to_float(panel_data.get('Ancho', 0))
            midclamp = 0.021
            espacio_borde_X = 1.0
            espacio_borde_Y = 1.0

            if orientacion.lower() == "landscape":
                largo_panel, ancho_panel = ancho_panel, largo_panel

            espacio_util_X = medida_X - 2 * espacio_borde_X
            espacio_util_Y = medida_Y - 2 * espacio_borde_Y

            paneles_totales_X = math.floor((espacio_util_X + midclamp) / (ancho_panel + midclamp))
            columnas_totales = math.ceil(paneles_totales_X / 30)

            paneles_por_fila = math.floor((espacio_util_X / columnas_totales + midclamp) / (ancho_panel + midclamp))
            paneles_por_fila = max(1, min(paneles_por_fila, 30))

            filas_por_columna = math.floor(espacio_util_Y / largo_panel)
            filas_por_columna = max(1, filas_por_columna)

            largo_total_fila = (paneles_por_fila * ancho_panel) + ((paneles_por_fila - 1) * midclamp)

            separacion_columnas = medida_X - (largo_total_fila * columnas_totales) - (2 * espacio_borde_X)

            if filas_por_columna > 1:
                separacion_filas = (espacio_util_Y - (largo_panel * filas_por_columna)) / (filas_por_columna - 1)
            else:
                separacion_filas = 0

            total_paneles = paneles_por_fila * filas_por_columna * columnas_totales

            return {
                'paneles_fila': f"{paneles_por_fila} Paneles",
                'paneles_columna': f"{filas_por_columna} Paneles",
                'paneles_array': f"{total_paneles} Paneles",
                'largo_fila': f"{largo_total_fila:.2f} Metros",
                'separacion_columnas': f"{separacion_columnas:.2f} Metros",
                'separacion_filas': f"{separacion_filas:.2f} Metros",
                'filas_x_columna': str(filas_por_columna),
                'columnas': str(columnas_totales),
                'total_filas_array': str(filas_por_columna * columnas_totales),
                'espacio_utilizado': f"X: {medida_X:.2f}m, Y: {medida_Y:.2f}m",
                'espacio_bordes': f"{espacio_borde_X:.2f}m cada lado",
                'diseno': f"Configuración: {columnas_totales} columnas x {filas_por_columna} filas"
            }

        except Exception as e:
            st.error(f"Error en cálculo: {str(e)}")
            return default_result
    
    def mostrar_pestana(self):
        st.header("☀️ Distribución Solar")
        
        if 'equipamiento_seleccionado' not in self.session_state:
            st.warning("⚠️ Primero seleccione un panel solar en la pestaña de Equipamientos")
            return
            
        panel_seleccionado = self.session_state.equipamiento_seleccionado.get('Paneles Solares')
        
        if not panel_seleccionado:
            st.warning("⚠️ Primero seleccione un panel solar en la pestaña de Equipamientos")
            return
        
        panel_data = self.equipamiento_manager.df_equipamientos['Paneles Solares'][
            self.equipamiento_manager.df_equipamientos['Paneles Solares']['nombre_display'] == panel_seleccionado
        ].iloc[0].to_dict()
        
        st.subheader("Especificaciones")
        st.markdown("""
        <style>
        .specs-table {
            width: 100%;
            border-collapse: collapse;
        }
        .specs-table th, .specs-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .specs-table th {
            background-color: #f2f2f2;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <table class="specs-table">
            <tr>
                <th>Dimensiones de Panel</th>
                <th>Especificación</th>
                <th>Medidas</th>
            </tr>
            <tr>
                <td>Largo</td>
                <td>Media Portrait (Y)</td>
                <td>{panel_data.get('Alto', '')} M</td>
            </tr>
            <tr>
                <td>Ancho</td>
                <td>Media Landscape (X)</td>
                <td>{panel_data.get('Ancho', '')} M</td>
            </tr>
            <tr>
                <td>Espesor</td>
                <td>Espesor del panel</td>
                <td>{panel_data.get('Espesor', '0.000')} M</td>
            </tr>
            <tr>
                <td>Área</td>
                <td>(Largo X Ancho)</td>
                <td>{self.formatear_decimal(panel_data.get('Metros²', 0), 3)} M²</td>
            </tr>
            <tr>
                <td>Watts</td>
                <td>Capacidad Nominal del panel</td>
                <td>{int(float(panel_data.get('Capacidad', 0)))} W</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        try:
            num_arrays = int(float(self.session_state.cliente_data.get("Arrays", "0"))) or 0
            num_arrays = max(0, min(num_arrays, 8))
        except:
            num_arrays = 0
        
        if num_arrays == 0:
            st.warning("No hay arrays configurados. Configure al menos un array en la pestaña de Datos del Cliente.")
            return
        
        total_paneles = 0
        total_potencia = 0.0
        panel_noct = math.ceil(float(panel_data.get('NOCT', 0)))
        
        for i in range(1, num_arrays + 1):
            array_index = i - 1

            # ✅ Verificar que arrays_config existe y es una lista
            if 'arrays_config' not in self.session_state.distribucion_data or not isinstance(self.session_state.distribucion_data['arrays_config'], list):
                self.session_state.distribucion_data['arrays_config'] = []

            while len(self.session_state.distribucion_data['arrays_config']) <= array_index:
                self.session_state.distribucion_data['arrays_config'].append({
                    'orientacion': 'Portrait',  # Inicializar con valor predeterminado
                    'largo_fila': 0.0,
                    'filas_x_columna': 0,
                    'columnas': 0,
                    'paneles_por_fila': 0,
                    'total_paneles': 0,
                    'total_filas_array': 0,
                    'medida_x': 0.0,
                    'medida_y': 0.0
                })
            
            current_config = self.session_state.distribucion_data['arrays_config'][array_index]
            
            # Recuperar orientación guardada o usar 'Portrait' como predeterminado
            orientacion = st.selectbox(
                f"Orientación del panel para Array {i}",
                options=['Portrait', 'Landscape'],
                index=0 if current_config.get('orientacion', 'Portrait') == 'Portrait' else 1,
                key=f"orientacion_array_{i}"
            )
            
            medida_x = self.session_state.array_data.get(f"Array_{i}_X", "0")
            medida_y = self.session_state.array_data.get(f"Array_{i}_Y", "0")
            
            distribucion = self.calcular_distribucion_paneles(
                panel_data,
                medida_x,
                medida_y,
                orientacion
            )

            # Guardar configuración con orientación
            array_config = {
                'orientacion': orientacion,
                'largo_fila': float(distribucion['largo_fila'].split()[0]),
                'filas_x_columna': int(distribucion['filas_x_columna']),
                'columnas': int(distribucion['columnas']),
                'paneles_por_fila': int(distribucion['paneles_fila'].split()[0]),
                'total_paneles': int(distribucion['paneles_array'].split()[0]),
                'paneles_array': int(distribucion['paneles_array'].split()[0]),  # NUEVO CAMPO
                'total_filas_array': int(distribucion['total_filas_array']),
                'medida_x': float(medida_x),
                'medida_y': float(medida_y)
            }
            
            if len(self.session_state.distribucion_data['arrays_config']) > array_index:
                self.session_state.distribucion_data['arrays_config'][array_index] = array_config
            else:
                self.session_state.distribucion_data['arrays_config'].append(array_config)

            paneles_array = array_config['total_paneles']
            total_paneles += paneles_array
            total_potencia += paneles_array * panel_noct
            
            st.subheader(f"Array {i}")
            st.markdown("""
            <style>
            .dist-table {
                width: 100%;
                border-collapse: collapse;
            }
            .dist-table th, .dist-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .dist-table th {
                background-color: #f2f2f6;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <table class="dist-table">
                <tr>
                    <th>Layout</th>
                    <th>Datos</th>
                </tr>
                <tr>
                    <td>Orientación</td>
                    <td>{orientacion}</td>
                </tr>
                <tr>
                    <td>Azimuth</td>
                    <td>{self.session_state.distribucion_data.get('layout_data', {}).get('azimuth', '')}</td>
                </tr>
                <tr>
                    <td>Pitch</td>
                    <td>{self.session_state.distribucion_data.get('layout_data', {}).get('pitch', '')}</td>
                </tr>
                <tr>
                    <td>Ground Clearance</td>
                    <td>{self.session_state.distribucion_data.get('layout_data', {}).get('ground_clearence', '')}</td>
                </tr>
                <tr>
                    <td>Espacio de bordes</td>
                    <td>{self.session_state.distribucion_data.get('layout_data', {}).get('espacio_bordes', '')}</td>
                </tr>
                <tr>
                    <td>Medida X</td>
                    <td>{medida_x} Metros</td>
                </tr>
                <tr>
                    <td>Medida Y</td>
                    <td>{medida_y} Metros</td>
                </tr>
                <tr>
                    <td>Cantidad de Filas X Columna</td>
                    <td>{distribucion['filas_x_columna']}</td>
                </tr>
                <tr>
                    <td>Cantidad de Columnas</td>
                    <td>{distribucion['columnas']}</td>
                </tr>
                <tr>
                    <td>Total de filas en Array</td>
                    <td>{distribucion['total_filas_array']}</td>
                </tr>
                <tr>
                    <td>Cantidad de Paneles por Fila</td>
                    <td>{distribucion['paneles_fila']}</td>
                </tr>
                <tr>
                    <td>Cantidad de Paneles por Columna</td>
                    <td>{distribucion['paneles_columna']}</td>
                </tr>
                <tr>   
                    <td>Largo de Fila</td>
                    <td>{distribucion['largo_fila']}</td>
                </tr>
                <tr>
                    <td>Separación entre Columnas</td>
                    <td>{distribucion['separacion_columnas']}</td>
                </tr>
                <tr>
                    <td>Separación entre Filas</td>
                    <td>{distribucion['separacion_filas']}</td>
                </tr>
                <tr>
                    <td>Max Paneles por Array</td>
                    <td>{paneles_array} Paneles</td>
                </tr>
            </table>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        self.session_state.distribucion_data['total_paneles'] = total_paneles
        self.session_state.distribucion_data['total_potencia'] = total_potencia
        
        st.subheader("Totales")
        col1, col2 = st.columns(2)
        col1.metric("Total Paneles", total_paneles)
        col2.metric("Potencia Total", f"{int(total_potencia)} W")