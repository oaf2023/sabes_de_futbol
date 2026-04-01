# Nombre: banner_sabesdefutbol_f13.py
# Fecha: 29 de mayo de 2024
# Utilidad: Generación de banner para X.com con estética retro, logo, QR y anuncio de "Fecha 13".
# Función/API: Procesamiento local de imágenes (Pillow). No se conecta a APIs externas.
#
# Descripción:
# Este script realiza la composición de una imagen de 1500x500px. Coloca el logo en el centro,
# un código QR en la parte inferior escoltado por redes sociales y URL, y un título superior
# "Proximamente Fecha 13" con letras en distintos tonos de azul. Aplica un filtro de ruido
# y color para simular fotografía de los años 70/80. 
# Implementa ejecución concurrente para versiones de Python superiores a 3.13.
#
# Ejemplo de resultado: Un archivo 'banner_x_fecha13.png' con estilo vintage y tipografía colorida.

import sys
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import concurrent.futures

def es_python_nuevo():
    """Verifica si la versión de Python es 3.13 o superior para usar concurrencia optimizada."""
    return sys.version_info[0] > 3 or (sys.version_info[0] == 3 and sys.version_info[1] >= 13)

def aplicar_filtro_retro(img):
    """Aplica ajustes de color y grano para simular los años 70/80."""
    # Desaturación y tinte cálido
    enhancer_color = ImageEnhance.Color(img)
    img = enhancer_color.enhance(0.75)
    
    enhancer_con = ImageEnhance.Contrast(img)
    img = enhancer_con.enhance(1.2)
    
    # Añadir un poco de grano/ruido visual
    noise = Image.effect_noise(img.size, 15)
    noise = noise.convert("RGBA")
    img = img.convert("RGBA")
    img = Image.blend(img, noise, 0.05)
    
    return img.convert("RGB")

def cargar_y_redimensionar(ruta, size):
    """Carga una imagen y la ajusta al tamaño especificado."""
    if not os.path.exists(ruta):
        return None
    try:
        img = Image.open(ruta).convert("RGBA")
        img = img.resize(size, Image.Resampling.LANCZOS)
        return img
    except:
        return None

def crear_banner_completo():
    ancho, alto = 1500, 500
    path_logo = "logo.png"
    path_qr = "QR_SabesDeFutbol_Social.png"
    
    componentes = {}
    tareas = {
        "logo": (path_logo, (200, 200)),
        "qr": (path_qr, (90, 90))
    }

    # Lógica de concurrencia según versión de Python
    if es_python_nuevo():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futuros = {executor.submit(cargar_y_redimensionar, p, s): n for n, (p, s) in tareas.items()}
            for f in concurrent.futures.as_completed(futuros):
                componentes[futuros[f]] = f.result()
    else:
        for nombre, (path, size) in tareas.items():
            componentes[nombre] = cargar_y_redimensionar(path, size)

    # Crear el lienzo (Simulando cancha de fútbol retro)
    # Usamos un verde oscuro mate propio de las transmisiones antiguas
    banner = Image.new("RGB", (ancho, alto), (34, 55, 34))
    draw = ImageDraw.Draw(banner)
    
    # Dibujar gradas/tribuna simplificada al fondo
    draw.rectangle([0, 0, 1500, 200], fill=(50, 50, 60)) # Gradas oscuras
    for i in range(0, 1500, 40):
        draw.line([i, 0, i, 200], fill=(60, 60, 70), width=2) # Líneas de asientos

    # Aplicar filtro retro al fondo base
    banner = aplicar_filtro_retro(banner)
    draw = ImageDraw.Draw(banner) # Re-instanciar draw después del filtro

    # Título: "Proximamente Fecha 13" en gama de azules
    texto_titulo = "PROXIMAMENTE FECHA 13"
    try:
        # Intenta cargar una fuente impactante, si no usa la de sistema
        font_titulo = ImageFont.truetype("arialbd.ttf", 60)
        font_social = ImageFont.truetype("arial.ttf", 22)
    except:
        font_titulo = ImageFont.load_default()
        font_social = ImageFont.load_default()

    # Colores gama azul (Cian, Real, Naval, Celeste)
    gama_azules = [
        (0, 191, 255),  # DeepSkyBlue
        (65, 105, 225), # RoyalBlue
        (0, 0, 139),    # DarkBlue
        (30, 144, 255), # DodgerBlue
        (173, 216, 230) # LightBlue
    ]

    # Dibujar título caracter por caracter para el efecto multicolor
    pos_x = 380
    for char in texto_titulo:
        color = random.choice(gama_azules)
        # Sombra retro para legibilidad
        draw.text((pos_x + 3, 53), char, fill=(0, 0, 0), font=font_titulo)
        draw.text((pos_x, 50), char, fill=color, font=font_titulo)
        # Ajuste manual de espaciado según el caracter
        ancho_char = draw.textlength(char, font=font_titulo)
        pos_x += ancho_char

    # Pegar Logo en el centro
    if componentes.get("logo"):
        logo = componentes["logo"]
        banner.paste(logo, (ancho // 2 - 100, alto // 2 - 80), logo)

    # Pegar QR y textos inferiores
    if componentes.get("qr"):
        qr = componentes["qr"]
        y_qr = alto - 120
        x_qr = ancho // 2 - 45
        banner.paste(qr, (x_qr, y_qr), qr)
        
        # Textos laterales al QR
        draw.text((x_qr - 210, y_qr + 35), "@sabesdefutbol", fill="white", font=font_social)
        draw.text((x_qr + 110, y_qr + 35), "https://sabesdefutbol.com", fill="white", font=font_social)

    # Guardar final
    nombre_archivo = "banner_x_fecha13.png"
    banner.save(nombre_archivo)
    print(f"Archivo generado exitosamente: {nombre_archivo}")

if __name__ == "__main__":
    crear_banner_completo()