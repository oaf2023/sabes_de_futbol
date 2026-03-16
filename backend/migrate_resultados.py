"""
migrate_resultados.py
Crea la tabla 'resultados' en la base de datos existente.
Ejecutar una sola vez en PythonAnywhere:
    python migrate_resultados.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app import app, db
from models import ResultadoFecha  # noqa: F401 — solo para que SQLAlchemy la registre

with app.app_context():
    db.create_all()
    print("✅ Tabla 'resultados' creada (o ya existía).")
