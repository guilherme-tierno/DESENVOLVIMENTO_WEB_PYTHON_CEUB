from functools import wraps

from flask import flash, g, make_response, redirect, render_template, request, url_for
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
    verify_jwt_in_request,
)

from . import bp
from ...models import User


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Faça login para acessar esta página.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped_view


@bp.before_app_request
def load_logged_user():
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        g.user = User.query.get(user_id) if user_id else None
    except Exception:
        g.user = None


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            token = create_access_token(identity=user.id)
            response = make_response(redirect(url_for("pages.home")))
            set_access_cookies(response, token)
            flash("Login realizado com sucesso.", "success")
            return response

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("auth/login.html")


@bp.post("/logout")
def logout():
    response = make_response(redirect(url_for("auth.login")))
    unset_jwt_cookies(response)
    flash("Sessão encerrada.", "info")
    return response
