from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.password_service import hash_senha, verificar_senha

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_usuarios: dict[str, str] = {}


@auth_bp.route("/cadastro", methods=["POST"])
def cadastro():
    dados = request.get_json()
    email = dados.get("email", "").strip()
    senha = dados.get("senha", "")

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    if email in _usuarios:
        return jsonify({"erro": "Usuário já existe"}), 409

    _usuarios[email] = hash_senha(senha)
    return jsonify({"mensagem": f"Usuário {email} criado com sucesso"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    email = dados.get("email", "").strip()
    senha = dados.get("senha", "")

    hash_salvo = _usuarios.get(email)

    if not hash_salvo or not verificar_senha(hash_salvo, senha):
        return jsonify({"erro": "Credenciais inválidas"}), 401

    token = create_access_token(identity=email)
    return jsonify({"access_token": token}), 200


@auth_bp.route("/perfil", methods=["GET"])
@jwt_required()
def perfil():
    email = get_jwt_identity()
    return jsonify({"mensagem": f"Olá, {email}!", "email": email}), 200
