"""
auth.py — Autenticación JWT para Sabes de Fútbol

Proporciona:
  - create_jwt_token(dni)   → genera token firmado con expiración 7 días
  - verify_jwt_token(token) → valida el token y retorna (dni, error)
  - require_auth            → decorador Flask para proteger endpoints
"""

import os
from functools import wraps
from datetime import datetime, timedelta, timezone

import jwt
from flask import request, jsonify


def _get_secret():
    secret = os.getenv('JWT_SECRET_KEY', '')
    if not secret or 'cambiar' in secret.lower():
        raise RuntimeError(
            "JWT_SECRET_KEY no está configurada. "
            "Generá una clave segura con: python3 -c \"import secrets; print(secrets.token_hex(32))\""
        )
    return secret


def create_jwt_token(dni: str) -> str:
    """Genera un JWT firmado con HS256 válido por 7 días."""
    payload = {
        'sub': dni,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, _get_secret(), algorithm='HS256')


def verify_jwt_token(token: str):
    """
    Valida el JWT y retorna (dni, None) si es válido,
    o (None, mensaje_error) si no lo es.
    """
    try:
        payload = jwt.decode(token, _get_secret(), algorithms=['HS256'])
        return payload['sub'], None
    except jwt.ExpiredSignatureError:
        return None, 'Sesión expirada. Volvé a iniciar sesión.'
    except jwt.InvalidTokenError:
        return None, 'Token inválido.'


def require_auth(f):
    """
    Decorador para endpoints que requieren autenticación JWT.

    Extrae el token del header:  Authorization: Bearer <token>
    Si es válido, guarda el DNI del usuario en request.current_user_dni
    Si no, retorna 401.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autenticación requerido.'}), 401

        token = auth_header[len('Bearer '):]
        dni, error = verify_jwt_token(token)
        if error:
            return jsonify({'error': error}), 401

        request.current_user_dni = dni
        return f(*args, **kwargs)
    return decorated
