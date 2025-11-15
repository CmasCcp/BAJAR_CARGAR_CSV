import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import numpy as np
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Configurar matplotlib para mejor visualización
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

class AnalizadorDatosPorFecha:
    def __init__(self, datos_folder='datos'):
        self.datos_folder = datos_folder
        self.reportes_folder = 'reportes_por_dispositivo'
        self.crear_carpeta_reportes()
        
    def crear_carpeta_reportes(self):
        """Crear carpeta para guardar los reportes"""
        os.makedirs(self.reportes_folder, exist_ok=True)
        print(f"📁 Carpeta de reportes creada: {self.reportes_folder}")
    
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
    
    def analizar_datos_dispositivo(self, proyecto_id, dispositivo_nombre, fechas_datos):
        """Analiza los datos de un dispositivo específico"""
        datos_resumen = []
        todos_los_datos = []
        
        for fecha, archivos in fechas_datos.items():
            if not archivos:
                continue
                
            registros_fecha = 0
            fechas_medicion = []
            
            for archivo in archivos:
                try:
                    df = pd.read_csv(archivo)
                    registros_fecha += len(df)
                    todos_los_datos.append(df)
                    
                    # Extraer fechas de medición si existe la columna
                    if 'fecha' in df.columns:
                        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                        fechas_validas = df['fecha'].dropna()
                        fechas_medicion.extend(fechas_validas.tolist())
                        
                except Exception as e:
                    print(f"⚠️ Error leyendo {archivo}: {e}")
                    continue
            
            if fechas_medicion:
                fecha_min = min(fechas_medicion)
                fecha_max = max(fechas_medicion)
            else:
                fecha_min = fecha_max = None
            
            datos_resumen.append({
                'Carpeta_Fecha': fecha,
                'Archivos_CSV': len(archivos),
                'Total_Registros': registros_fecha,
                'Fecha_Min_Datos': fecha_min.strftime('%Y-%m-%d') if fecha_min else 'N/A',
                'Fecha_Max_Datos': fecha_max.strftime('%Y-%m-%d') if fecha_max else 'N/A'
            })
        
        # Crear DataFrame con el resumen
        df_resumen = pd.DataFrame(datos_resumen)
        
        # Combinar todos los datos para estadísticas generales
        if todos_los_datos:
            df_completo = pd.concat(todos_los_datos, ignore_index=True)
        else:
            df_completo = pd.DataFrame()
            
        return df_resumen, df_completo
    
    def crear_tabla_visual(self, df_resumen, dispositivo_nombre, proyecto_id, df_completo=None):
        """Crea una imagen con la tabla de resumen del dispositivo"""
        fig, axes = plt.subplots(2, 1, figsize=(16, 12))
        fig.suptitle(f'📊 Análisis de Datos - {dispositivo_nombre} (Proyecto {proyecto_id})', 
                     fontsize=16, fontweight='bold', y=0.95)
        
        # ===== TABLA DE RESUMEN POR FECHA =====
        ax1 = axes[0]
        ax1.axis('tight')
        ax1.axis('off')
        ax1.set_title('📅 Resumen por Carpeta de Fecha', fontsize=14, fontweight='bold', pad=20)
        
        if not df_resumen.empty:
            # Crear tabla
            table_data = []
            headers = ['Carpeta Fecha', 'Archivos CSV', 'Total Registros', 'Fecha Min Datos', 'Fecha Max Datos']
            
            for _, row in df_resumen.iterrows():
                table_data.append([
                    row['Carpeta_Fecha'],
                    f"{row['Archivos_CSV']:,}",
                    f"{row['Total_Registros']:,}",
                    row['Fecha_Min_Datos'],
                    row['Fecha_Max_Datos']
                ])
            
            # Agregar fila de totales
            total_archivos = df_resumen['Archivos_CSV'].sum()
            total_registros = df_resumen['Total_Registros'].sum()
            table_data.append([
                '📊 TOTAL',
                f"{total_archivos:,}",
                f"{total_registros:,}",
                '-',
                '-'
            ])
            
            # Crear la tabla
            table = ax1.table(cellText=table_data, colLabels=headers, 
                            cellLoc='center', loc='center',
                            colWidths=[0.2, 0.15, 0.15, 0.25, 0.25])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)
            
            # Estilizar la tabla
            for i in range(len(headers)):
                table[(0, i)].set_facecolor('#4CAF50')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            # Colorear la fila de totales
            for i in range(len(headers)):
                table[(len(table_data), i)].set_facecolor('#FFC107')
                table[(len(table_data), i)].set_text_props(weight='bold')
        else:
            ax1.text(0.5, 0.5, '❌ No hay datos disponibles', 
                    ha='center', va='center', transform=ax1.transAxes, fontsize=14)
        
        # ===== GRÁFICO DE REGISTROS POR FECHA =====
        ax2 = axes[1]
        ax2.set_title('📈 Distribución de Registros por Carpeta de Fecha', fontsize=14, fontweight='bold')
        
        if not df_resumen.empty and len(df_resumen) > 0:
            # Crear gráfico de barras
            bars = ax2.bar(range(len(df_resumen)), df_resumen['Total_Registros'], 
                          color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'][:len(df_resumen)])
            
            # Personalizar el gráfico
            ax2.set_xlabel('Carpeta de Fecha', fontweight='bold')
            ax2.set_ylabel('Cantidad de Registros', fontweight='bold')
            ax2.set_xticks(range(len(df_resumen)))
            ax2.set_xticklabels(df_resumen['Carpeta_Fecha'], rotation=45, ha='right')
            
            # Agregar valores encima de las barras
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):,}', ha='center', va='bottom', fontweight='bold')
            
            # Agregar grid
            ax2.grid(True, alpha=0.3, axis='y')
            ax2.set_axisbelow(True)
            
        else:
            ax2.text(0.5, 0.5, '❌ No hay datos para graficar', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=14)
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
        
        plt.tight_layout()
        
        # Guardar la imagen
        filename = f"reporte_{dispositivo_nombre}_proyecto_{proyecto_id}.png"
        filepath = os.path.join(self.reportes_folder, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='black')
        plt.close()
        
        return filepath
    
    def generar_resumen_general(self, estructura):
        """Genera un resumen general de todos los dispositivos"""
        resumen_general = []
        
        for proyecto_id, dispositivos in estructura.items():
            for dispositivo_nombre, fechas_datos in dispositivos.items():
                total_archivos = sum(len(archivos) for archivos in fechas_datos.values())
                total_carpetas_fecha = len(fechas_datos)
                
                # Calcular total de registros
                total_registros = 0
                for archivos in fechas_datos.values():
                    for archivo in archivos:
                        try:
                            df = pd.read_csv(archivo)
                            total_registros += len(df)
                        except:
                            continue
                
                resumen_general.append({
                    'Proyecto': proyecto_id,
                    'Dispositivo': dispositivo_nombre,
                    'Carpetas_Fecha': total_carpetas_fecha,
                    'Archivos_CSV': total_archivos,
                    'Total_Registros': total_registros
                })
        
        return pd.DataFrame(resumen_general)
    
    def crear_resumen_general_visual(self, df_resumen_general):
        """Crea una imagen con el resumen general de todos los dispositivos"""
        fig, axes = plt.subplots(2, 2, figsize=(20, 14))
        fig.suptitle('📊 RESUMEN GENERAL DE TODOS LOS DISPOSITIVOS', 
                     fontsize=18, fontweight='bold', y=0.95)
        
        # ===== TABLA RESUMEN GENERAL =====
        ax1 = axes[0, 0]
        ax1.axis('tight')
        ax1.axis('off')
        ax1.set_title('📋 Resumen por Dispositivo', fontsize=14, fontweight='bold')
        
        if not df_resumen_general.empty:
            # Preparar datos para la tabla
            table_data = []
            headers = ['Proyecto', 'Dispositivo', 'Carpetas Fecha', 'Archivos CSV', 'Total Registros']
            
            for _, row in df_resumen_general.iterrows():
                table_data.append([
                    row['Proyecto'],
                    row['Dispositivo'],
                    f"{row['Carpetas_Fecha']:,}",
                    f"{row['Archivos_CSV']:,}",
                    f"{row['Total_Registros']:,}"
                ])
            
            # Agregar totales
            total_dispositivos = len(df_resumen_general)
            total_carpetas = df_resumen_general['Carpetas_Fecha'].sum()
            total_archivos = df_resumen_general['Archivos_CSV'].sum()
            total_registros = df_resumen_general['Total_Registros'].sum()
            
            table_data.append([
                f'TOTAL ({total_dispositivos} dispositivos)',
                '-',
                f"{total_carpetas:,}",
                f"{total_archivos:,}",
                f"{total_registros:,}"
            ])
            
            # Crear tabla
            table = ax1.table(cellText=table_data, colLabels=headers,
                            cellLoc='center', loc='center',
                            colWidths=[0.15, 0.25, 0.2, 0.2, 0.2])
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.8)
            
            # Estilizar
            for i in range(len(headers)):
                table[(0, i)].set_facecolor('#2E7D32')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            # Fila de totales
            for i in range(len(headers)):
                table[(len(table_data), i)].set_facecolor('#FF9800')
                table[(len(table_data), i)].set_text_props(weight='bold')
        
        # ===== GRÁFICO DE REGISTROS POR DISPOSITIVO =====
        ax2 = axes[0, 1]
        ax2.set_title('📊 Registros por Dispositivo', fontsize=14, fontweight='bold')
        
        if not df_resumen_general.empty:
            dispositivos_labels = [f"{row['Dispositivo']}\n(P{row['Proyecto']})" for _, row in df_resumen_general.iterrows()]
            bars = ax2.bar(range(len(df_resumen_general)), df_resumen_general['Total_Registros'],
                          color=plt.cm.Set3(np.linspace(0, 1, len(df_resumen_general))))
            
            ax2.set_xlabel('Dispositivos', fontweight='bold')
            ax2.set_ylabel('Total de Registros', fontweight='bold')
            ax2.set_xticks(range(len(df_resumen_general)))
            ax2.set_xticklabels(dispositivos_labels, rotation=45, ha='right', fontsize=9)
            
            # Valores en las barras
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):,}', ha='center', va='bottom', fontsize=8, fontweight='bold')
            
            ax2.grid(True, alpha=0.3, axis='y')
        
        # ===== GRÁFICO DE ARCHIVOS POR DISPOSITIVO =====
        ax3 = axes[1, 0]
        ax3.set_title('📁 Archivos CSV por Dispositivo', fontsize=14, fontweight='bold')
        
        if not df_resumen_general.empty:
            bars = ax3.bar(range(len(df_resumen_general)), df_resumen_general['Archivos_CSV'],
                          color=plt.cm.Pastel1(np.linspace(0, 1, len(df_resumen_general))))
            
            ax3.set_xlabel('Dispositivos', fontweight='bold')
            ax3.set_ylabel('Cantidad de Archivos CSV', fontweight='bold')
            ax3.set_xticks(range(len(df_resumen_general)))
            ax3.set_xticklabels(dispositivos_labels, rotation=45, ha='right', fontsize=9)
            
            # Valores en las barras
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom', fontsize=8, fontweight='bold')
            
            ax3.grid(True, alpha=0.3, axis='y')
        
        # ===== DISTRIBUCIÓN POR PROYECTOS =====
        ax4 = axes[1, 1]
        ax4.set_title('🎯 Distribución por Proyectos', fontsize=14, fontweight='bold')
        
        if not df_resumen_general.empty:
            # Agrupar por proyecto
            por_proyecto = df_resumen_general.groupby('Proyecto').agg({
                'Total_Registros': 'sum',
                'Dispositivo': 'count'
            }).reset_index()
            
            # Crear gráfico de pie
            sizes = por_proyecto['Total_Registros'].values
            labels = [f"Proyecto {p}\n({row['Dispositivo']} dispositivos)\n{row['Total_Registros']:,} registros" 
                     for p, row in zip(por_proyecto['Proyecto'], por_proyecto.to_dict('records'))]
            
            colors = plt.cm.Set2(np.linspace(0, 1, len(por_proyecto)))
            
            wedges, texts, autotexts = ax4.pie(sizes, labels=labels, autopct='%1.1f%%',
                                              colors=colors, startangle=90)
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        # Guardar
        filepath = os.path.join(self.reportes_folder, "resumen_general_todos_dispositivos.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='black')
        plt.close()
        
        return filepath
    
    def ejecutar_analisis_completo(self):
        """Ejecuta el análisis completo de todos los dispositivos"""
        print("🚀 Iniciando análisis completo de datos por dispositivo...")
        
        # Escanear estructura
        estructura = self.escanear_estructura()
        
        if not estructura:
            print("❌ No se encontró estructura de datos válida")
            return
        
        # Analizar cada dispositivo
        reportes_generados = []
        datos_resumen_general = []
        
        for proyecto_id, dispositivos in estructura.items():
            for dispositivo_nombre, fechas_datos in dispositivos.items():
                print(f"\n📊 Analizando {dispositivo_nombre} (Proyecto {proyecto_id})...")
                
                # Analizar datos del dispositivo
                df_resumen, df_completo = self.analizar_datos_dispositivo(
                    proyecto_id, dispositivo_nombre, fechas_datos
                )
                
                # Crear tabla visual
                reporte_path = self.crear_tabla_visual(
                    df_resumen, dispositivo_nombre, proyecto_id, df_completo
                )
                
                reportes_generados.append(reporte_path)
                print(f"✅ Reporte generado: {reporte_path}")
                
                # Agregar al resumen general
                if not df_resumen.empty:
                    datos_resumen_general.append({
                        'Proyecto': proyecto_id,
                        'Dispositivo': dispositivo_nombre,
                        'Carpetas_Fecha': len(fechas_datos),
                        'Archivos_CSV': df_resumen['Archivos_CSV'].sum(),
                        'Total_Registros': df_resumen['Total_Registros'].sum()
                    })
        
        # Crear resumen general
        if datos_resumen_general:
            df_resumen_general = pd.DataFrame(datos_resumen_general)
            resumen_general_path = self.crear_resumen_general_visual(df_resumen_general)
            print(f"\n✅ Resumen general generado: {resumen_general_path}")
            reportes_generados.append(resumen_general_path)
        
        print(f"\n🎉 Análisis completado! Se generaron {len(reportes_generados)} reportes en la carpeta '{self.reportes_folder}'")
        
        return reportes_generados


# ===== EJECUCIÓN PRINCIPAL =====
if __name__ == "__main__":
    analizador = AnalizadorDatosPorFecha()
    reportes = analizador.ejecutar_analisis_completo()
    
    if reportes:
        print("\n📋 REPORTES GENERADOS:")
        for i, reporte in enumerate(reportes, 1):
            print(f"{i}. {reporte}")
    else:
        print("\n❌ No se pudieron generar reportes")