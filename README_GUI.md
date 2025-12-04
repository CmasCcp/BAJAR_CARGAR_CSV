# 🌡️ Interfaz Gráfica para Colector de Datos de Sensores

## 📖 Descripción

Esta interfaz gráfica proporciona una manera fácil e intuitiva de configurar y ejecutar la colección de datos de sensores ambientales. Está diseñada para simplificar el uso del script `app.py`.

## 🚀 Instalación y Uso

### Requisitos
- Python 3.7 o superior
- Tkinter (incluido con Python)
- Dependencias de `app.py` (requests, etc.)

### Ejecución
```bash
python colector_gui.py
```

## 🎯 Características Principales

### 📁 Configuración de Archivos
- **Config JSON**: Selecciona el archivo de configuración de dispositivos
- **Carpeta Salida**: Define dónde se guardarán los datos descargados

### 🔧 Gestión de Dispositivos
- **Agregar**: Crear nuevos dispositivos con formulario intuitivo
- **Editar**: Modificar dispositivos existentes
- **Eliminar**: Remover dispositivos de la configuración
- **Guardar**: Persistir cambios en el archivo JSON

### 🚀 Ejecución de Colección
- **Inicio Fácil**: Botón para iniciar la colección con un click
- **Progreso Visual**: Barra de progreso e indicadores de estado
- **Ejecución Segura**: Procesos en segundo plano sin bloquear la interfaz

### 📋 Monitoreo
- **Logs en Tiempo Real**: Registro detallado de todas las operaciones
- **Estados Visuales**: Indicadores claros del estado del proceso
- **Resultados**: Resumen de archivos creados y estadísticas

## 🎨 Interfaz de Usuario

### Secciones Principales

1. **📁 Configuración de Archivos**
   - Campos para seleccionar archivos y carpetas
   - Botones de navegación integrados

2. **🔧 Gestión de Dispositivos**
   - Tabla con lista de dispositivos configurados
   - Botones para operaciones CRUD (Crear, Leer, Actualizar, Eliminar)

3. **🚀 Ejecución de Colección**
   - Botón principal de ejecución
   - Barra de progreso
   - Indicador de estado

4. **📋 Registro de Actividad**
   - Área de logs con scroll automático
   - Timestamps para cada acción
   - Botón para limpiar historial

### Diálogo de Dispositivo

Al agregar o editar un dispositivo, se abre un formulario con:
- **Proyecto**: Número o nombre del proyecto
- **Código Interno**: Identificador único del dispositivo
- **URL API**: Endpoint completo para obtener datos
- **Última Fecha**: Fecha desde la cual obtener datos (formato YYYY-MM-DD)

## 📊 Formato de Configuración JSON

```json
[
    {
        "proyecto": 12,
        "codigo_interno": "AIRE-01", 
        "api_url": "https://api.ejemplo.com/dispositivo/AIRE-01/datos",
        "ultima_fecha": "2025-11-20"
    },
    {
        "proyecto": 13,
        "codigo_interno": "LVAG-05",
        "api_url": "https://api.ejemplo.com/dispositivo/LVAG-05/datos",
        "ultima_fecha": "2025-11-25"
    }
]
```

### Campos Obligatorios
- `proyecto`: Identificador del proyecto (número o string)
- `codigo_interno`: Código único del dispositivo

### Campos Opcionales
- `api_url`: URL de la API (requerida para la colección)
- `ultima_fecha`: Fecha base para filtrar datos nuevos

## 🔧 Funcionalidades Avanzadas

### Validación de Datos
- Verificación de campos obligatorios
- Formato de fechas
- URLs válidas

### Manejo de Errores
- Mensajes informativos de error
- Recuperación graceful de fallos
- Logs detallados para depuración

### Seguridad
- Confirmaciones para acciones destructivas
- Validación antes de ejecutar colecciones
- Manejo seguro de hilos de ejecución

## 🛠️ Solución de Problemas

### Problemas Comunes

1. **Error de módulos no encontrados**
   ```bash
   pip install requests pandas
   ```

2. **Archivos no se crean**
   - Verificar permisos de la carpeta de salida
   - Comprobar conectividad de red para URLs API
   - Revisar logs para detalles del error

3. **Configuración no se guarda**
   - Verificar permisos de escritura en el directorio
   - Comprobar que la ruta del archivo JSON sea válida

4. **Interfaz no responde**
   - La colección se ejecuta en segundo plano
   - Esperar a que termine o cerrar si es necesario

## 🎯 Mejores Prácticas

1. **Configuración**
   - Usar rutas absolutas cuando sea posible
   - Mantener backups de archivos de configuración
   - Validar URLs antes de guardar

2. **Ejecución**
   - Verificar conectividad antes de ejecutar colecciones masivas
   - Monitorear los logs durante la ejecución
   - No cerrar la aplicación durante colecciones activas

3. **Mantenimiento**
   - Limpiar logs periódicamente
   - Actualizar fechas base según necesidades
   - Revisar configuración de dispositivos regularmente

## 📞 Soporte

Para problemas o sugerencias:
- Revisar los logs de la aplicación
- Verificar la configuración de dispositivos
- Comprobar conectividad de red
- Consultar documentación de `app.py`