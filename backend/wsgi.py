"""
wsgi.py — Entry point para PythonAnywhere WSGI

Configurar en el panel Web de PythonAnywhere:
  Source code:    /home/<usuario>/sabes_de_futbol/backend
  Working dir:    /home/<usuario>/sabes_de_futbol/backend
  WSGI file:      este archivo (wsgi.py)

Variables de entorno (panel Web → Environment variables):
  JWT_SECRET_KEY   → clave larga y aleatoria
  ADMIN_SECRET     → clave para el panel admin
"""

import sys
import os

# Directorio del backend (donde vive este archivo y app.py)
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Raíz del proyecto (necesaria para servir index.html, style.css, js/, etc.)
project_root = os.path.abspath(os.path.join(backend_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app as application  # PythonAnywhere busca 'application'
