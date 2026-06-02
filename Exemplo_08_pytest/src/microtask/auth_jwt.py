"""Helpers para emitir e validar tokens JWT.

Token contém:
  sub:  id do usuário (string)
  role: role do usuário
  exp:  timestamp UTC de expiração
  iat:  timestamp UTC de emissão

`token_required(view)` é o decorator que protege rotas JSON. Ele:
  - exige header `Authorization: Bearer <token>`
  - decodifica o token usando SECRET_KEY
  - injeta `g.current_user` (instância de User) no contexto da requisição
  - retorna 401 em qualquer falha (faltando, inválido, expirado)

Política importante:
  - Token expirado, inválido, ausente: TODOS retornam 401, sem detalhar.
    Diferenciar facilita ataque (enumeration). Logs internos podem detalhar,
    a resposta HTTP não.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from .models import User


def gerar_token(user: User) -> str:
    """Emite um JWT assinado para o usuário."""
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "iat": agora,
        "exp": agora
        + timedelta(minutes=current_app.config["JWT_EXPIRES_MINUTES"]),
    }
    token = jwt.encode(
        payload, current_app.config["SECRET_KEY"], algorithm="HS256"
    )
    # PyJWT 2.x retorna str; mantemos como str
    return token


def decodificar_token(token: str) -> dict:
    """Decodifica e valida o token; levanta jwt.PyJWTError em falha."""
    return jwt.decode(
        token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
    )


def token_required(view):
    """Protege rotas que esperam Authorization: Bearer <token>."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "token ausente"}), 401

        token = header.removeprefix("Bearer ").strip()
        if not token:
            return jsonify({"error": "token ausente"}), 401

        try:
            payload = decodificar_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token expirado"}), 401
        except jwt.PyJWTError:
            return jsonify({"error": "token inválido"}), 401

        user = User.query.get(int(payload["sub"]))
        if user is None:
            return jsonify({"error": "token inválido"}), 401

        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    """Composta com token_required: exige que current_user tenha um dos roles."""

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if user is None or user.role not in roles:
                return jsonify({"error": "acesso negado"}), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator
