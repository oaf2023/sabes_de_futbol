# Nombre: ean13_generator.py
# Fecha: 2025-11-25
# Utilidad: Generación de códigos EAN-13 válidos con cálculo de dígito de control.
# Conectado a API: No, utiliza la lógica matemática estándar de GS1.
# Descripción: Calcula el 13vo dígito (checksum) de una cadena de 12 números 
# para formar un EAN-13 legal y genera la imagen correspondiente.
# Ejemplo de devolución: "Código generado: 7791234567891 - Imagen: ean13_valido.png"

import sys
import threading

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    print("Error: Instale las dependencias: pip install python-barcode Pillow setuptools")
    sys.exit(1)

def calcular_digito_control(primeros_12_digitos):
    """
    Calcula el dígito de control EAN-13 usando el algoritmo estándar:
    1. Sumar dígitos en posiciones impares.
    2. Sumar dígitos en posiciones pares y multiplicar por 3.
    3. Sumar ambos resultados y buscar el múltiplo de 10 superior.
    """
    try:
        numeros = [int(d) for d in primeros_12_digitos]
        par = sum(numeros[1::2]) * 3
        impar = sum(numeros[0::2])
        total = par + impar
        digito = (10 - (total % 10)) % 10
        return str(digito)
    except ValueError:
        return None

def proceso_generacion_ean(doce_digitos, nombre_archivo):
    """
    Genera el código EAN completo y crea la imagen.
    """
    digito = calcular_digito_control(doce_digitos)
    if digito is None:
        print("Error: Los 12 dígitos deben ser solo números.")
        return

    ean_completo = doce_digitos + digito
    
    try:
        EAN = barcode.get_barcode_class('ean13')
        visual_options = {
            'module_width': 0.4,
            'module_height': 15.0,
            'font_size': 12,
            'text_distance': 4.0,
        }
        
        mi_barcode = EAN(ean_completo, writer=ImageWriter())
        archivo_final = mi_barcode.save(nombre_archivo, options=visual_options)
        print(f"Código EAN-13 puro generado: {ean_completo}")
        print(f"Imagen guardada en: {archivo_final}")
    except Exception as e:
        print(f"Error al generar imagen: {e}")

def ejecutar_sistema_ean(doce_digitos, nombre_archivo):
    """
    Punto de entrada con gestión de concurrencia para Python 3.13+
    """
    print(f"Verificando entorno... Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Bandera para versiones 3.13 o superiores
    if sys.version_info.major == 3 and sys.version_info.minor >= 13:
        print("Estado: Ejecución Multihilo activa.")
        t = threading.Thread(target=proceso_generacion_ean, args=(doce_digitos, nombre_archivo))
        t.start()
        t.join()
    else:
        print("Estado: Ejecución secuencial normal.")
        proceso_generacion_ean(doce_digitos, nombre_archivo)

if __name__ == "__main__":
    # IMPORTANTE: Para que la tienda lo acepte, usa un prefijo válido (ej: 779 para Argentina)
    # Proporciona exactamente 12 dígitos:
    MIS_12_DIGITOS = "779123456789" 
    ejecutar_sistema_ean(MIS_12_DIGITOS, "ean13_puro_valido")