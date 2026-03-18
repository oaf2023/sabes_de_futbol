"""
Nombre: game_logic.py
Fecha: 2026-03-04
Versión: 2.0
Creador: OAF
Propósito: Helpers para codificación bitstring (L/E/V) y lógica de aciertos con soporte dinámico.
Funcionamiento: Provee funciones para transformar listas de selecciones en cadenas binarias, decodificarlas, generar resultados aleatorios y calcular aciertos.
Fuentes de datos: Recibe listas de objetos/strings desde el backend (app.py).
Ejemplo de uso: 
    bitstring = codificar_jugada(['L', 'E', 'V'], n=3)
    aciertos = calcular_aciertos_bin(jugada_bin, resultado_bin, n=13)
"""

import random

RESULTADOS_POSIBLES = ['L', 'E', 'V']

# Probabilidades más realistas (local gana más seguido)
PROBABILIDADES = {
    'L': 0.45,  # Local gana
    'E': 0.28,  # Empate
    'V': 0.27,  # Visitante gana
}

def codificar_jugada(selecciones):
    """
    Convierte una lista de resultados ['L', 'E', 'V'] en un bitstring.
    'L' -> '100', 'E' -> '010', 'V' -> '001'
    """
    mapeo = {'L': '100', 'E': '010', 'V': '001'}
    bitstring = ""
    for s in selecciones:
        bitstring += mapeo.get(s, '000')
    return bitstring

def decodificar_jugada(bitstring):
    """
    Convierte un bitstring en una lista de resultados ['L', 'E', 'V'].
    Toma bloques de 3 caracteres. No tiene límite fijo.
    """
    selecciones = []
    for i in range(0, len(bitstring), 3):
        bloque = bitstring[i:i+3]
        if len(bloque) < 3: break
        
        if bloque == '100': selecciones.append('L')
        elif bloque == '010': selecciones.append('E')
        elif bloque == '001': selecciones.append('V')
        else: selecciones.append(None)
        
    return selecciones

def generar_resultados_aleatorios_bin(n=13):
    """
    Genera un bitstring de resultados aleatorios basado en probabilidades.
    """
    selecciones = []
    pesos = [PROBABILIDADES['L'], PROBABILIDADES['E'], PROBABILIDADES['V']]
    for _ in range(n):
        res = random.choices(RESULTADOS_POSIBLES, weights=pesos, k=1)[0]
        selecciones.append(res)
    return codificar_jugada(selecciones)

def calcular_aciertos_bin(jugada_bin, resultado_bin):
    """
    Compara dos bitstrings y cuenta cuántos bloques de 3 coinciden.
    Usa la longitud mínima para evitar errores si las cadenas difieren.
    """
    aciertos = 0
    min_len = min(len(jugada_bin), len(resultado_bin))
    for i in range(0, min_len, 3):
        bloque_j = jugada_bin[i:i+3]
        bloque_r = resultado_bin[i:i+3]
        if bloque_j == bloque_r and ('1' in bloque_j):
            aciertos += 1
    return aciertos
