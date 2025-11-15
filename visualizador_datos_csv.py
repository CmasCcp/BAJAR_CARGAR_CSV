import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Configurar matplotlib para mejor visualización
plt.rcParams['figure.figsize'] = (20, 12)
plt.rcParams['font.size'] = 9
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

class VisualizadorDatosCSV:
    def __init__(self, datos_folder='datos'):
        self.datos_folder = datos_folder
        self.tablas_folder = 'tablas_datos_dispositivos'
        self.crear_carpeta_tablas()
        
    def crear_carpeta_tablas(self):
        """Crear carpeta para guardar las tablas de datos"""
        os.makedirs(self.tablas_folder, exist_ok=True)
        print(f"📁 Carpeta de tablas creada: {self.tablas_folder}")
    
    def escanear_estructura(self):
        """Escanea la estructura de carpetas proyecto/dispositivo/fecha"""
        estructura = {}
        
        if not os.path.exists(self.datos_folder):
            print(f"❌ No existe la carpeta: {self.datos_folder}")
            return estructura
            
        # Buscar proyectos (proyecto_X)
        for proyecto_folder in glob.glob(os.path.join(self.datos_folder, "proyecto_*")):
            proyecto_nombre = os.path.basename(proyecto_folder)
            proyecto_id = proyecto_nombre.replace("proyecto_", "")
            
            estructura[proyecto_id] = {}
            
            # Buscar dispositivos dentro del proyecto
            for dispositivo_folder in glob.glob(os.path.join(proyecto_folder, "*")):
                if os.path.isdir(dispositivo_folder):
                    dispositivo_nombre = os.path.basename(dispositivo_folder)
                    estructura[proyecto_id][dispositivo_nombre] = {}
                    
                    # Buscar carpetas de fechas dentro del dispositivo
                    for fecha_folder in glob.glob(os.path.join(dispositivo_folder, "*")):
                        if os.path.isdir(fecha_folder):
                            fecha_nombre = os.path.basename(fecha_folder)
                            
                            # Buscar archivos CSV en la carpeta de fecha
                            archivos_csv = glob.glob(os.path.join(fecha_folder, "*.csv"))
                            estructura[proyecto_id][dispositivo_nombre][fecha_nombre] = archivos_csv
        
        return estructura
    
    def leer_datos_dispositivo(self, proyecto_id, dispositivo_nombre, fechas_datos, limite_filas=1000):
        """Lee todos los datos CSV de un dispositivo y los combina"""
        todos_los_datos = []
        archivos_procesados = []
        
        for fecha, archivos in fechas_datos.items():
            for archivo in archivos:
                try:
                    df = pd.read_csv(archivo)
                    
                    # Agregar información de contexto
                    df['archivo_origen'] = os.path.basename(archivo)
                    df['fecha_carpeta'] = fecha
                    df['dispositivo'] = dispositivo_nombre
                    df['proyecto'] = proyecto_id
                    
                    todos_los_datos.append(df)
                    archivos_procesados.append(archivo)
                    
                    print(f"📄 Leído: {os.path.basename(archivo)} ({len(df)} registros)")
                    
                except Exception as e:
                    print(f"⚠️ Error leyendo {archivo}: {e}")
                    continue
        
        if todos_los_datos:
            df_completo = pd.concat(todos_los_datos, ignore_index=True)
            
            # Limitar número de filas para visualización
            if len(df_completo) > limite_filas:
                print(f"📊 Limitando visualización a {limite_filas} registros (total: {len(df_completo)})")
                df_muestra = df_completo.head(limite_filas)
                info_adicional = f"Mostrando {limite_filas} de {len(df_completo)} registros totales"
            else:
                df_muestra = df_completo
                info_adicional = f"Mostrando todos los {len(df_completo)} registros"
            
            return df_muestra, len(archivos_procesados), info_adicional
        else:
            return pd.DataFrame(), 0, "No hay datos disponibles"
    
    def crear_tabla_datos_visual(self, df, dispositivo_nombre, proyecto_id, info_adicional, archivos_count):
        """Crea una imagen con la tabla de datos del dispositivo"""
        
        if df.empty:
            # Crear imagen para datos vacíos
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            ax.text(0.5, 0.5, f'❌ No hay datos disponibles para {dispositivo_nombre}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            plt.title(f'📊 Datos de {dispositivo_nombre} (Proyecto {proyecto_id})', 
                     fontsize=16, fontweight='bold')
            
            filename = f"tabla_datos_{dispositivo_nombre}_proyecto_{proyecto_id}.png"
            filepath = os.path.join(self.tablas_folder, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            return filepath
        
        # Preparar datos para visualización
        df_display = df.copy()
        
        # Formatear fechas si existen
        for col in df_display.columns:
            if 'fecha' in col.lower():
                try:
                    df_display[col] = pd.to_datetime(df_display[col], errors='coerce')
                    df_display[col] = df_display[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
        
        # Limitar ancho de texto para visualización
        for col in df_display.select_dtypes(include=['object']).columns:
            df_display[col] = df_display[col].astype(str).apply(
                lambda x: x[:30] + '...' if len(x) > 30 else x
            )
        
        # Determinar número de filas por página
        filas_por_pagina = 25
        total_filas = len(df_display)
        num_paginas = max(1, (total_filas + filas_por_pagina - 1) // filas_por_pagina)
        
        archivos_generados = []
        
        for pagina in range(num_paginas):
            inicio = pagina * filas_por_pagina
            fin = min((pagina + 1) * filas_por_pagina, total_filas)
            df_pagina = df_display.iloc[inicio:fin]
            
            # Crear figura
            fig = plt.figure(figsize=(20, 14))
            gs = fig.add_gridspec(3, 1, height_ratios=[0.1, 0.1, 0.8])
            
            # Título principal
            ax_titulo = fig.add_subplot(gs[0, :])
            ax_titulo.text(0.5, 0.5, 
                          f'📊 DATOS DE {dispositivo_nombre.upper()} (PROYECTO {proyecto_id})',
                          ha='center', va='center', fontsize=18, fontweight='bold',
                          transform=ax_titulo.transAxes)
            ax_titulo.axis('off')
            
            # Información adicional
            ax_info = fig.add_subplot(gs[1, :])
            info_texto = (f"📄 {archivos_count} archivos procesados | "
                         f"{info_adicional} | "
                         f"Página {pagina + 1} de {num_paginas} | "
                         f"Filas {inicio + 1}-{fin} de {total_filas}")
            ax_info.text(0.5, 0.5, info_texto,
                        ha='center', va='center', fontsize=12,
                        transform=ax_info.transAxes, style='italic')
            ax_info.axis('off')
            
            # Tabla de datos
            ax_tabla = fig.add_subplot(gs[2, :])
            ax_tabla.axis('tight')
            ax_tabla.axis('off')
            
            if not df_pagina.empty:
                # Preparar datos para la tabla
                headers = list(df_pagina.columns)
                cell_text = []
                
                for idx, row in df_pagina.iterrows():
                    cell_text.append([str(val) for val in row])
                
                # Crear tabla
                table = ax_tabla.table(cellText=cell_text, 
                                     colLabels=headers,
                                     cellLoc='center', 
                                     loc='center')
                
                # Configurar tabla
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                table.scale(1, 2)
                
                # Estilizar headers
                num_cols = len(headers)
                for i in range(num_cols):
                    table[(0, i)].set_facecolor('#1976D2')
                    table[(0, i)].set_text_props(weight='bold', color='white')
                    table[(0, i)].set_height(0.08)
                
                # Alternar colores de filas
                for i in range(1, len(cell_text) + 1):
                    for j in range(num_cols):
                        if i % 2 == 0:
                            table[(i, j)].set_facecolor('#F5F5F5')
                        else:
                            table[(i, j)].set_facecolor('#FFFFFF')
                        table[(i, j)].set_height(0.06)
                
                # Ajustar ancho de columnas
                cellDict = table.get_celld()
                for key, cell in cellDict.items():
                    cell.set_linewidth(0.5)
                    
            else:
                ax_tabla.text(0.5, 0.5, 'No hay datos para mostrar', 
                            ha='center', va='center', transform=ax_tabla.transAxes)
            
            plt.tight_layout()
            
            # Guardar página
            if num_paginas > 1:
                filename = f"tabla_datos_{dispositivo_nombre}_proyecto_{proyecto_id}_pagina_{pagina + 1}.png"
            else:
                filename = f"tabla_datos_{dispositivo_nombre}_proyecto_{proyecto_id}.png"
            
            filepath = os.path.join(self.tablas_folder, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='black')
            plt.close()
            
            archivos_generados.append(filepath)
            print(f"✅ Tabla generada: {filename}")
        
        return archivos_generados
    
    def crear_resumen_columnas(self, estructura):
        """Crea un resumen de las columnas disponibles en todos los dispositivos"""
        resumen_columnas = {}
        
        for proyecto_id, dispositivos in estructura.items():
            for dispositivo_nombre, fechas_datos in dispositivos.items():
                columnas_dispositivo = set()
                
                for fecha, archivos in fechas_datos.items():
                    for archivo in archivos:
                        try:
                            df = pd.read_csv(archivo, nrows=1)  # Solo leer headers
                            columnas_dispositivo.update(df.columns.tolist())
                        except:
                            continue
                
                resumen_columnas[f"{dispositivo_nombre} (P{proyecto_id})"] = list(columnas_dispositivo)
        
        return resumen_columnas
    
    def crear_imagen_resumen_columnas(self, resumen_columnas):
        """Crea una imagen con el resumen de columnas por dispositivo"""
        if not resumen_columnas:
            return None
            
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        ax.axis('tight')
        ax.axis('off')
        
        # Preparar datos para la tabla
        max_columnas = max(len(cols) for cols in resumen_columnas.values()) if resumen_columnas else 0
        
        headers = ['Dispositivo'] + [f'Columna {i+1}' for i in range(max_columnas)]
        cell_text = []
        
        for dispositivo, columnas in resumen_columnas.items():
            fila = [dispositivo] + columnas + [''] * (max_columnas - len(columnas))
            cell_text.append(fila)
        
        # Crear tabla
        table = ax.table(cellText=cell_text, colLabels=headers,
                        cellLoc='left', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Estilizar
        num_cols = len(headers)
        for i in range(num_cols):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Alternar colores
        for i in range(1, len(cell_text) + 1):
            for j in range(num_cols):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#F5F5F5')
                else:
                    table[(i, j)].set_facecolor('#FFFFFF')
        
        plt.title('📋 RESUMEN DE COLUMNAS POR DISPOSITIVO', 
                 fontsize=16, fontweight='bold', pad=20)
        
        filename = 'resumen_columnas_dispositivos.png'
        filepath = os.path.join(self.tablas_folder, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filepath
    
    def ejecutar_visualizacion_completa(self, limite_filas=500):
        """Ejecuta la visualización completa de datos de todos los dispositivos"""
        print("🚀 Iniciando visualización de datos CSV por dispositivo...")
        
        # Escanear estructura
        estructura = self.escanear_estructura()
        
        if not estructura:
            print("❌ No se encontró estructura de datos válida")
            return
        
        # Crear resumen de columnas
        print("\n📋 Creando resumen de columnas...")
        resumen_columnas = self.crear_resumen_columnas(estructura)
        resumen_path = self.crear_imagen_resumen_columnas(resumen_columnas)
        if resumen_path:
            print(f"✅ Resumen de columnas: {resumen_path}")
        
        # Procesar cada dispositivo
        tablas_generadas = []
        
        for proyecto_id, dispositivos in estructura.items():
            for dispositivo_nombre, fechas_datos in dispositivos.items():
                print(f"\n📊 Procesando datos de {dispositivo_nombre} (Proyecto {proyecto_id})...")
                
                # Leer datos del dispositivo
                df_datos, archivos_count, info_adicional = self.leer_datos_dispositivo(
                    proyecto_id, dispositivo_nombre, fechas_datos, limite_filas
                )
                
                # Crear tablas visuales
                archivos_tabla = self.crear_tabla_datos_visual(
                    df_datos, dispositivo_nombre, proyecto_id, info_adicional, archivos_count
                )
                
                if isinstance(archivos_tabla, list):
                    tablas_generadas.extend(archivos_tabla)
                else:
                    tablas_generadas.append(archivos_tabla)
        
        if resumen_path:
            tablas_generadas.insert(0, resumen_path)
        
        print(f"\n🎉 Visualización completada! Se generaron {len(tablas_generadas)} tablas en '{self.tablas_folder}'")
        
        return tablas_generadas


# ===== EJECUCIÓN PRINCIPAL =====
if __name__ == "__main__":
    print("🔍 Iniciando visualización de datos CSV...")
    
    visualizador = VisualizadorDatosCSV()
    tablas = visualizador.ejecutar_visualizacion_completa(limite_filas=500)
    
    if tablas:
        print("\n📋 TABLAS GENERADAS:")
        for i, tabla in enumerate(tablas, 1):
            print(f"{i}. {os.path.basename(tabla)}")
    else:
        print("\n❌ No se pudieron generar tablas")