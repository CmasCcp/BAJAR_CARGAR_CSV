#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz Gráfica para Colector de Datos de Sensores
Autor: Sistema de Colección de Datos
Fecha: Diciembre 2025
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import threading
from datetime import datetime
import sys
from app import obtener_datos_desde_api, LOCAL_FOLDER

class ColectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌡️ Colector de Datos C+")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.config_path = tk.StringVar(value="config.json")
        self.output_folder = tk.StringVar(value=LOCAL_FOLDER)
        self.dispositivos = []
        self.ejecutando = False
        
        # Configurar estilo
        self.configurar_estilos()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar configuración inicial
        self.cargar_config_existente()
        
    def configurar_estilos(self):
        """Configurar estilos visuales"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 11, 'bold'), foreground='#34495e')
        style.configure('Success.TButton', background='#27ae60', foreground='white')
        style.configure('Warning.TButton', background='#e67e22', foreground='white')
        style.configure('Danger.TButton', background='#e74c3c', foreground='white')
        
    def crear_interfaz(self):
        """Crear la interfaz principal"""
        # Frame principal con scrollbar
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # ========== TÍTULO ==========
        titulo = ttk.Label(main_frame, text="🌡️ Colector de Datos C+", style='Title.TLabel')
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # ========== CONFIGURACIÓN DE ARCHIVOS ==========
        config_frame = ttk.LabelFrame(main_frame, text="📁 Configuración de Archivos", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Archivo de configuración
        ttk.Label(config_frame, text="Config JSON:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(config_frame, textvariable=self.config_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(config_frame, text="Examinar", command=self.seleccionar_config).grid(row=0, column=2)
        
        # Carpeta de salida
        ttk.Label(config_frame, text="Carpeta Salida:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        ttk.Entry(config_frame, textvariable=self.output_folder, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        ttk.Button(config_frame, text="Examinar", command=self.seleccionar_carpeta).grid(row=1, column=2, pady=(5, 0))
        
        # ========== GESTIÓN DE DISPOSITIVOS ==========
        dispositivos_frame = ttk.LabelFrame(main_frame, text="🔧 Gestión de Dispositivos", padding="10")
        dispositivos_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        dispositivos_frame.columnconfigure(0, weight=1)
        dispositivos_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Botones de gestión
        botones_frame = ttk.Frame(dispositivos_frame)
        botones_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(botones_frame, text="➕ Agregar Dispositivo", command=self.agregar_dispositivo).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(botones_frame, text="✏️ Editar Seleccionado", command=self.editar_dispositivo).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(botones_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_dispositivo, style='Danger.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(botones_frame, text="💾 Guardar Config", command=self.guardar_config, style='Success.TButton').pack(side=tk.RIGHT)
        
        # Lista de dispositivos
        columns = ('Proyecto', 'Código Interno', 'URL API', 'Última Fecha')
        self.tree_dispositivos = ttk.Treeview(dispositivos_frame, columns=columns, show='headings', height=8)
        
        # Configurar columnas
        for col in columns:
            self.tree_dispositivos.heading(col, text=col)
            self.tree_dispositivos.column(col, width=120)
        
        self.tree_dispositivos.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para la lista
        scrollbar = ttk.Scrollbar(dispositivos_frame, orient=tk.VERTICAL, command=self.tree_dispositivos.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree_dispositivos.configure(yscrollcommand=scrollbar.set)
        
        # ========== EJECUCIÓN ==========
        ejecucion_frame = ttk.LabelFrame(main_frame, text="🚀 Ejecución de Colección", padding="10")
        ejecucion_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        ejecucion_frame.columnconfigure(0, weight=1)
        
        # Botón principal de ejecución
        self.btn_ejecutar = ttk.Button(ejecucion_frame, text="🚀 Iniciar Colección de Datos", 
                                       command=self.ejecutar_coleccion, style='Success.TButton')
        self.btn_ejecutar.grid(row=0, column=0, pady=(0, 10))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(ejecucion_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Estado
        self.label_estado = ttk.Label(ejecucion_frame, text="✅ Listo para ejecutar", foreground='green')
        self.label_estado.grid(row=2, column=0, pady=(0, 10))
        
        # ========== LOGS ==========
        logs_frame = ttk.LabelFrame(main_frame, text="📋 Registro de Actividad", padding="10")
        logs_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Área de logs
        self.text_logs = scrolledtext.ScrolledText(logs_frame, height=8, width=80)
        self.text_logs.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botón para limpiar logs
        ttk.Button(logs_frame, text="🗑️ Limpiar Logs", command=self.limpiar_logs).grid(row=1, column=0, pady=(5, 0))
        
    def log_mensaje(self, mensaje):
        """Agregar mensaje al área de logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_logs.insert(tk.END, f"[{timestamp}] {mensaje}\n")
        self.text_logs.see(tk.END)
        self.root.update_idletasks()
        
    def limpiar_logs(self):
        """Limpiar el área de logs"""
        self.text_logs.delete(1.0, tk.END)
        
    def seleccionar_config(self):
        """Seleccionar archivo de configuración"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de configuración",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if filename:
            self.config_path.set(filename)
            self.cargar_config_existente()
            
    def seleccionar_carpeta(self):
        """Seleccionar carpeta de salida"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.output_folder.set(folder)
            
    def cargar_config_existente(self):
        """Cargar configuración existente si existe"""
        try:
            if os.path.exists(self.config_path.get()):
                with open(self.config_path.get(), 'r', encoding='utf-8') as f:
                    self.dispositivos = json.load(f)
                self.actualizar_lista_dispositivos()
                self.log_mensaje(f"✅ Configuración cargada: {len(self.dispositivos)} dispositivos")
            else:
                self.dispositivos = []
                self.actualizar_lista_dispositivos()
                self.log_mensaje("ℹ️ Archivo de configuración no encontrado. Se creará uno nuevo.")
        except Exception as e:
            self.log_mensaje(f"❌ Error cargando configuración: {e}")
            self.dispositivos = []
            self.actualizar_lista_dispositivos()
            
    def actualizar_lista_dispositivos(self):
        """Actualizar la lista visual de dispositivos"""
        # Limpiar lista actual
        for item in self.tree_dispositivos.get_children():
            self.tree_dispositivos.delete(item)
            
        # Agregar dispositivos
        for dispositivo in self.dispositivos:
            self.tree_dispositivos.insert('', tk.END, values=(
                dispositivo.get('proyecto', 'N/A'),
                dispositivo.get('codigo_interno', 'N/A'),
                dispositivo.get('api_url', 'N/A')[:50] + '...' if len(dispositivo.get('api_url', '')) > 50 else dispositivo.get('api_url', 'N/A'),
                dispositivo.get('ultima_fecha', 'N/A')
            ))
            
    def agregar_dispositivo(self):
        """Agregar nuevo dispositivo"""
        self.abrir_dialogo_dispositivo()
        
    def editar_dispositivo(self):
        """Editar dispositivo seleccionado"""
        seleccion = self.tree_dispositivos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un dispositivo para editar.")
            return
            
        indice = self.tree_dispositivos.index(seleccion[0])
        dispositivo = self.dispositivos[indice]
        self.abrir_dialogo_dispositivo(dispositivo, indice)
        
    def eliminar_dispositivo(self):
        """Eliminar dispositivo seleccionado"""
        seleccion = self.tree_dispositivos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un dispositivo para eliminar.")
            return
            
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este dispositivo?"):
            indice = self.tree_dispositivos.index(seleccion[0])
            del self.dispositivos[indice]
            self.actualizar_lista_dispositivos()
            self.log_mensaje("🗑️ Dispositivo eliminado")
            
    def abrir_dialogo_dispositivo(self, dispositivo=None, indice=None):
        """Abrir diálogo para agregar/editar dispositivo"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Dispositivo" if not dispositivo else "Editar Dispositivo")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Variables del diálogo
        proyecto_var = tk.StringVar(value=dispositivo.get('proyecto', '') if dispositivo else '')
        codigo_var = tk.StringVar(value=dispositivo.get('codigo_interno', '') if dispositivo else '')
        url_var = tk.StringVar(value=dispositivo.get('api_url', '') if dispositivo else '')
        fecha_var = tk.StringVar(value=dispositivo.get('ultima_fecha', '') if dispositivo else '')
        
        # Campos del formulario
        ttk.Label(dialog, text="Proyecto:", style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        ttk.Entry(dialog, textvariable=proyecto_var, width=40).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Código Interno:", style='Subtitle.TLabel').grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        ttk.Entry(dialog, textvariable=codigo_var, width=40).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="URL API:", style='Subtitle.TLabel').grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        url_entry = tk.Text(dialog, height=4, width=40, wrap=tk.WORD)
        url_entry.grid(row=2, column=1, padx=10, pady=10)
        if dispositivo:
            url_entry.insert(1.0, dispositivo.get('api_url', ''))
        
        ttk.Label(dialog, text="Última Fecha (YYYY-MM-DD):", style='Subtitle.TLabel').grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        ttk.Entry(dialog, textvariable=fecha_var, width=40).grid(row=3, column=1, padx=10, pady=10)
        
        # Botones
        botones_frame = ttk.Frame(dialog)
        botones_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def guardar():
            # Validaciones básicas
            if not proyecto_var.get() or not codigo_var.get():
                messagebox.showerror("Error", "Proyecto y Código Interno son obligatorios.")
                return
                
            nuevo_dispositivo = {
                'proyecto': int(proyecto_var.get()) if proyecto_var.get().isdigit() else proyecto_var.get(),
                'codigo_interno': codigo_var.get(),
                'api_url': url_entry.get(1.0, tk.END).strip(),
                'ultima_fecha': fecha_var.get() if fecha_var.get() else None
            }
            
            # Limpiar campos vacíos
            nuevo_dispositivo = {k: v for k, v in nuevo_dispositivo.items() if v is not None and v != ''}
            
            if indice is not None:
                # Editar existente
                self.dispositivos[indice] = nuevo_dispositivo
                self.log_mensaje(f"✏️ Dispositivo {codigo_var.get()} actualizado")
            else:
                # Agregar nuevo
                self.dispositivos.append(nuevo_dispositivo)
                self.log_mensaje(f"➕ Dispositivo {codigo_var.get()} agregado")
                
            self.actualizar_lista_dispositivos()
            dialog.destroy()
            
        def cancelar():
            dialog.destroy()
            
        ttk.Button(botones_frame, text="💾 Guardar", command=guardar, style='Success.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(botones_frame, text="❌ Cancelar", command=cancelar).pack(side=tk.LEFT)
        
    def guardar_config(self):
        """Guardar configuración actual"""
        try:
            with open(self.config_path.get(), 'w', encoding='utf-8') as f:
                json.dump(self.dispositivos, f, indent=4, ensure_ascii=False)
            self.log_mensaje(f"💾 Configuración guardada en {self.config_path.get()}")
            messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
        except Exception as e:
            self.log_mensaje(f"❌ Error guardando configuración: {e}")
            messagebox.showerror("Error", f"No se pudo guardar la configuración:\n{e}")
            
    def ejecutar_coleccion(self):
        """Ejecutar colección de datos"""
        if self.ejecutando:
            messagebox.showwarning("Advertencia", "Ya hay una colección en proceso.")
            return
            
        if not self.dispositivos:
            messagebox.showwarning("Advertencia", "No hay dispositivos configurados.")
            return
            
        # Guardar configuración antes de ejecutar
        self.guardar_config()
        
        # Cambiar estado
        self.ejecutando = True
        self.btn_ejecutar.config(state='disabled', text="🔄 Ejecutando...")
        self.label_estado.config(text="🔄 Ejecutando colección...", foreground='orange')
        self.progress.start()
        
        # Ejecutar en hilo separado
        def ejecutar():
            try:
                self.log_mensaje("🚀 Iniciando colección de datos...")
                
                # Usar la función de app.py
                archivos_creados = obtener_datos_desde_api(
                    config_path=self.config_path.get(),
                    output_folder=self.output_folder.get()
                )
                
                # Resultados
                if archivos_creados:
                    self.log_mensaje(f"🎉 Colección completada exitosamente!")
                    self.log_mensaje(f"📁 {len(archivos_creados)} archivos guardados")
                    for archivo in archivos_creados:
                        self.log_mensaje(f"   • {archivo}")
                        
                    # Actualizar estado en la UI
                    self.root.after(0, lambda: self.label_estado.config(
                        text=f"✅ Completado: {len(archivos_creados)} archivos", 
                        foreground='green'
                    ))
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Éxito", 
                        f"Colección completada!\n{len(archivos_creados)} archivos creados."
                    ))
                else:
                    self.log_mensaje("ℹ️ No se crearon nuevos archivos")
                    self.log_mensaje("   (Todos los dispositivos ya están actualizados)")
                    self.root.after(0, lambda: self.label_estado.config(
                        text="ℹ️ Sin nuevos datos", 
                        foreground='blue'
                    ))
                    
            except Exception as e:
                self.log_mensaje(f"❌ Error durante la colección: {e}")
                self.root.after(0, lambda: self.label_estado.config(
                    text="❌ Error en colección", 
                    foreground='red'
                ))
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    f"Error durante la colección:\n{e}"
                ))
            finally:
                # Restaurar estado
                self.root.after(0, self.finalizar_ejecucion)
                
        # Iniciar hilo
        threading.Thread(target=ejecutar, daemon=True).start()
        
    def finalizar_ejecucion(self):
        """Finalizar proceso de ejecución"""
        self.ejecutando = False
        self.btn_ejecutar.config(state='normal', text="🚀 Iniciar Colección de Datos")
        self.progress.stop()


def main():
    """Función principal de la GUI"""
    root = tk.Tk()
    app = ColectorGUI(root)
    
    # Configurar cierre de ventana
    def on_closing():
        if app.ejecutando:
            if messagebox.askokcancel("Salir", "Hay una colección en proceso. ¿Deseas cerrar de todas formas?"):
                root.destroy()
        else:
            root.destroy()
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Iniciar aplicación
    root.mainloop()


if __name__ == "__main__":
    main()