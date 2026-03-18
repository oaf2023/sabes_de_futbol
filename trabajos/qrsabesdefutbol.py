# Nombre: qr_generator_social.py
# Fecha: 2026-03-13
# Utilidad: Generador de códigos QR de alta resolución para marketing en redes sociales.
# Conectado a API: No, utiliza la librería local qrcode con soporte para imágenes PIL.
# Descripción: Genera un código QR optimizado para el sitio "https://savesdefutbol.com".
# Si se detecta Python 3.13+, la generación se realiza de forma concurrente mediante hilos.
# Ejemplo de devolución: Archivo 'QR_SavesDeFutbol_Social.png' creado exitosamente.

import sys
import threading

try:
    import qrcode
except ImportError:
    print("Error: La librería 'qrcode' no está instalada. Ejecute: pip install qrcode[pil]")
    sys.exit(1)

def crear_qr_logic(url, nombre_archivo):
    """
    Lógica de renderizado del QR con parámetros de corrección de errores alta
    para asegurar que se lea bien incluso en pantallas de celulares.
    """
    try:
        # Configuración del QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H, # Alta corrección
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Crear la imagen (Colores personalizados: Negro sobre Blanco)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar archivo
        output_path = f"{nombre_archivo}.png"
        img.save(output_path)
        print(f"Éxito: QR para '{url}' generado como '{output_path}'.")
    except Exception as e:
        print(f"Error en el proceso de creación: {e}")

def generar_recurso_qr(url_sitio, archivo_salida):
    """
    Punto de entrada con gestión de concurrencia según versión de Python.
    """
    print(f"Iniciando generador en Python {sys.version_info.major}.{sys.version_info.minor}")

    # Bandera para ejecución concurrente en Python 3.13 o superior
    if sys.version_info.major == 3 and sys.version_info.minor >= 13:
        print("Modo: Concurrente (Threading habilitado para v3.13+)")
        proceso = threading.Thread(target=crear_qr_logic, args=(url_sitio, archivo_salida))
        proceso.start()
        proceso.join()
    else:
        print("Modo: Secuencial (Versión inferior a 3.13)")
        crear_qr_logic(url_sitio, archivo_salida)

if __name__ == "__main__":
    # URL solicitada por el usuario
    URL_DESTINO = "https://www.sabesdefutbol.com"
    NOMBRE_FILE = "QR_SabesDeFutbol_Social"
    
    generar_recurso_qr(URL_DESTINO, NOMBRE_FILE)