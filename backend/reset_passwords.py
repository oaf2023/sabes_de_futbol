"""
Reset de contraseñas de los usuarios existentes.
Ejecutar desde: c:\\sabes_de_futbol\\backend
    python reset_passwords.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Usuario

NUEVAS_PASSWORDS = {
    '12345678': 'clave1234',   # usuario de prueba
    '16695057': 'oscar1234',   # Oscar Fontana
}

with app.app_context():
    for dni, nueva_clave in NUEVAS_PASSWORDS.items():
        u = db.session.get(Usuario, dni)
        if u:
            u.set_password(nueva_clave)
            db.session.commit()
            print(f"✅ Contraseña de {dni} ({u.nombre or 'sin nombre'}) reseteada a: {nueva_clave}")
        else:
            print(f"❌ Usuario {dni} no encontrado")
