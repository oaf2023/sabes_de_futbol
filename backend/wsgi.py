"""
wsgi.py — Entry point para PythonAnywhere WSGI

En PythonAnywhere, configurar la Web App así:
  Source code:    /home/<tu_usuario>/sabes_de_futbol/backend
  Working dir:    /home/<tu_usuario>/sabes_de_futbol/backend
  WSGI file:      este archivo (wsgi.py)
  Python path:    /home/<tu_usuario>/sabes_de_futbol/backend
"""

import sys
import os

# Agregar el directorio del backend al path de Python
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from app import app as application  # PythonAnywhere busca 'application'
