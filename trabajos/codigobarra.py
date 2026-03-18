# Nombre: generator_barcode.py
# Fecha: 2026-03-13
# Utilidad: Genera una imagen de código de barras (Code 128) para activos del sistema.
# Conectado a API: No (Usa la librería local 'python-barcode' y 'Pillow').
# Descripción: Crea un archivo .png con un código de barras basado en un ID. 
# Si la versión es >= 3.13, procesa la generación en un hilo separado.
# Ejemplo de devolución: Archivo 'barcode_logo_sabes.png' guardado exitosamente.

import sys
import threading
import barcode
from barcode.writer import ImageWriter

def procesar_generacion(data_string, filename):
    """
    Lógica interna para generar el archivo de imagen del código de barras.
    """
    try:
        # Usamos Code128 que permite caracteres alfanuméricos
        code_class = barcode.get_barcode_class('code128')
        my_barcode = code_class(data_string, writer=ImageWriter())
        
        # Guardamos la imagen
        fullname = my_barcode.save(filename)
        print(f"Resultado: Código de barras guardado como '{fullname}'")
        return fullname
    except Exception as e:
        print(f"Error en la generación: {e}")
        return None

def generar_codigo_barra(id_activo, nombre_archivo):
    # Verificación de versión para ejecución concurrente (Regla 3.13)
    if sys.version_info >= (3, 13):
        print(f"Sistema detectado: Python {sys.version_info.major}.{sys.version_info.minor}")
        print("Ejecutando generación en hilo concurrente...")
        hilo = threading.Thread(target=procesar_generacion, args=(id_activo, nombre_archivo))
        hilo.start()
        hilo.join() # Esperamos para asegurar la creación en este ejemplo
    else:
        print(f"Sistema detectado: Python {sys.version_info.major}.{sys.version_info.minor}")
        print("Ejecutando generación normal (secuencial)...")
        procesar_generacion(id_activo, nombre_archivo)

if __name__ == "__main__":
    # Ejemplo de uso: Generar un código para el logo o una boleta
    # ID: SDF-LOGO-2026 (Sabes De Futbol - Logo)
    generar_codigo_barra("SDF-LOGO-2026", "barcode_sabes_futbol")