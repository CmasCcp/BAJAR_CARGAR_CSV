import pandas as pd
import os
import glob
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
import warnings
warnings.filterwarnings('ignore')

class GeneradorPDFDispositivos:
    def __init__(self, datos_folder='datos'):
        self.datos_folder = datos_folder
        self.pdfs_folder = 'reportes_pdf_dispositivos'
        self.crear_carpeta_pdfs()
        self.styles = getSampleStyleSheet()
        self.configurar_estilos()
        
    def crear_carpeta_pdfs(self):
        """Crear carpeta para guardar los PDFs"""
        os.makedirs(self.pdfs_folder, exist_ok=True)
        print(f"📁 Carpeta de PDFs creada: {self.pdfs_folder}")
    
    def configurar_estilos(self):
        """Configurar estilos personalizados para el PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.darkblue,
            alignment=1  # Centro
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.darkgreen,
            alignment=1  # Centro
        )
        
        self.info_style = ParagraphStyle(
            'InfoStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            textColor=colors.black,
            alignment=1  # Centro
        )
    
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
    
    def leer_datos_dispositivo(self, proyecto_id, dispositivo_nombre, fechas_datos):
        """Lee todos los datos CSV de un dispositivo y los combina"""
        todos_los_datos = []
        archivos_procesados = []
        info_archivos = []
        
        for fecha, archivos in fechas_datos.items():
            for archivo in archivos:
                try:
                    df = pd.read_csv(archivo)
                    
                    # Agregar información de contexto
                    df['📁 Carpeta'] = fecha
                    df['📄 Archivo'] = os.path.basename(archivo)
                    
                    todos_los_datos.append(df)
                    archivos_procesados.append(archivo)
                    info_archivos.append({
                        'archivo': os.path.basename(archivo),
                        'fecha_carpeta': fecha,
                        'registros': len(df)
                    })
                    
                    print(f"📄 Leído: {os.path.basename(archivo)} ({len(df)} registros)")
                    
                except Exception as e:
                    print(f"⚠️ Error leyendo {archivo}: {e}")
                    continue
        
        if todos_los_datos:
            df_completo = pd.concat(todos_los_datos, ignore_index=True)
            return df_completo, info_archivos
        else:
            return pd.DataFrame(), []
    
    def formatear_datos_para_tabla(self, df):
        """Formatea los datos para mostrar mejor en el PDF"""
        df_display = df.copy()
        
        # Formatear fechas
        for col in df_display.columns:
            if 'fecha' in col.lower():
                try:
                    df_display[col] = pd.to_datetime(df_display[col], errors='coerce')
                    df_display[col] = df_display[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                    # Limpiar valores NaT
                    df_display[col] = df_display[col].fillna('N/A')
                except:
                    pass
        
        # Limitar longitud de texto
        for col in df_display.select_dtypes(include=['object']).columns:
            df_display[col] = df_display[col].astype(str).apply(
                lambda x: x[:25] + '...' if len(x) > 25 else x
            )
        
        # Reemplazar NaN con valores más legibles
        df_display = df_display.fillna('N/A')
        
        return df_display
    
    def crear_tabla_pdf(self, df, ancho_disponible):
        """Crea una tabla ReportLab a partir del DataFrame"""
        if df.empty:
            return None
        
        # Preparar datos
        headers = list(df.columns)
        data = [headers]  # Primera fila: headers
        
        # Agregar filas de datos
        for _, row in df.iterrows():
            data.append([str(val) for val in row])
        
        # Calcular ancho de columnas dinámicamente
        num_cols = len(headers)
        col_width = ancho_disponible / num_cols
        
        # Crear tabla
        table = Table(data, colWidths=[col_width] * num_cols)
        
        # Aplicar estilos
        table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            
            # Data rows style
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        return table
    
    def crear_pdf_dispositivo(self, proyecto_id, dispositivo_nombre, df_datos, info_archivos):
        """Crea un PDF completo para un dispositivo"""
        
        filename = f"reporte_{dispositivo_nombre}_proyecto_{proyecto_id}.pdf"
        filepath = os.path.join(self.pdfs_folder, filename)
        
        # Usar landscape para más espacio
        doc = SimpleDocTemplate(filepath, pagesize=landscape(A4),
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Contenido del PDF
        story = []
        
        # TÍTULO PRINCIPAL
        title = f"📊 REPORTE DE DATOS - {dispositivo_nombre.upper()}"
        story.append(Paragraph(title, self.title_style))
        
        # SUBTÍTULO
        subtitle = f"Proyecto {proyecto_id} | Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        story.append(Paragraph(subtitle, self.subtitle_style))
        
        story.append(Spacer(1, 20))
        
        # RESUMEN DE ARCHIVOS
        if info_archivos:
            total_registros = sum(info['registros'] for info in info_archivos)
            total_archivos = len(info_archivos)
            
            resumen_text = (f"📄 <b>{total_archivos}</b> archivos procesados | "
                          f"📊 <b>{total_registros:,}</b> registros totales | "
                          f"📅 Carpetas de fechas: <b>{len(set(info['fecha_carpeta'] for info in info_archivos))}</b>")
            story.append(Paragraph(resumen_text, self.info_style))
            story.append(Spacer(1, 15))
            
            # Tabla de resumen de archivos
            archivo_data = [['📄 Archivo', '📅 Fecha Carpeta', '📊 Registros']]
            for info in info_archivos:
                archivo_data.append([
                    info['archivo'],
                    info['fecha_carpeta'],
                    f"{info['registros']:,}"
                ])
            
            archivo_table = Table(archivo_data, colWidths=[4*inch, 2*inch, 1*inch])
            archivo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(archivo_table)
            story.append(Spacer(1, 20))
        
        # DATOS PRINCIPALES
        if not df_datos.empty:
            story.append(Paragraph("📋 DATOS COMPLETOS", self.subtitle_style))
            story.append(Spacer(1, 10))
            
            # Formatear datos
            df_formatted = self.formatear_datos_para_tabla(df_datos)
            
            # Dividir en páginas si hay muchos datos
            filas_por_pagina = 35  # Ajustado para landscape
            total_filas = len(df_formatted)
            
            if total_filas <= filas_por_pagina:
                # Todos los datos en una página
                ancho_disponible = landscape(A4)[0] - 1*inch  # Restar márgenes
                table = self.crear_tabla_pdf(df_formatted, ancho_disponible)
                if table:
                    story.append(table)
            else:
                # Dividir en múltiples páginas
                for pagina in range(0, total_filas, filas_por_pagina):
                    fin = min(pagina + filas_por_pagina, total_filas)
                    df_pagina = df_formatted.iloc[pagina:fin]
                    
                    if pagina > 0:
                        story.append(PageBreak())
                    
                    page_title = f"📋 DATOS COMPLETOS - Página {pagina//filas_por_pagina + 1} (Filas {pagina + 1}-{fin})"
                    story.append(Paragraph(page_title, self.subtitle_style))
                    story.append(Spacer(1, 10))
                    
                    ancho_disponible = landscape(A4)[0] - 1*inch
                    table = self.crear_tabla_pdf(df_pagina, ancho_disponible)
                    if table:
                        story.append(table)
                    
                    if pagina + filas_por_pagina < total_filas:
                        story.append(Spacer(1, 20))
        
        else:
            story.append(Paragraph("❌ No hay datos disponibles para este dispositivo", self.info_style))
        
        # Construir PDF
        doc.build(story)
        return filepath
    
    def generar_todos_los_pdfs(self):
        """Genera PDFs para todos los dispositivos"""
        print("🚀 Iniciando generación de PDFs por dispositivo...")
        
        # Escanear estructura
        estructura = self.escanear_estructura()
        
        if not estructura:
            print("❌ No se encontró estructura de datos válida")
            return []
        
        pdfs_generados = []
        
        for proyecto_id, dispositivos in estructura.items():
            for dispositivo_nombre, fechas_datos in dispositivos.items():
                print(f"\n📊 Generando PDF para {dispositivo_nombre} (Proyecto {proyecto_id})...")
                
                # Leer datos del dispositivo
                df_datos, info_archivos = self.leer_datos_dispositivo(
                    proyecto_id, dispositivo_nombre, fechas_datos
                )
                
                # Crear PDF
                pdf_path = self.crear_pdf_dispositivo(
                    proyecto_id, dispositivo_nombre, df_datos, info_archivos
                )
                
                pdfs_generados.append(pdf_path)
                print(f"✅ PDF generado: {os.path.basename(pdf_path)}")
        
        print(f"\n🎉 Generación completada! Se crearon {len(pdfs_generados)} PDFs en '{self.pdfs_folder}'")
        return pdfs_generados


# ===== EJECUCIÓN PRINCIPAL =====
if __name__ == "__main__":
    print("📄 Iniciando generación de reportes PDF...")
    
    generador = GeneradorPDFDispositivos()
    pdfs = generador.generar_todos_los_pdfs()
    
    if pdfs:
        print("\n📋 PDFs GENERADOS:")
        for i, pdf in enumerate(pdfs, 1):
            print(f"{i}. {os.path.basename(pdf)}")
        print(f"\n📁 Ubicación: {os.path.abspath(generador.pdfs_folder)}")
    else:
        print("\n❌ No se pudieron generar PDFs")