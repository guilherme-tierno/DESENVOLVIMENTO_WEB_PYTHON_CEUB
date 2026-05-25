from functools import wraps

from flask import flash, g, redirect, render_template, request, session, url_for

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
    user_id = session.get("user_id")
    g.user = User.query.get(user_id) if user_id else None


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Login realizado com sucesso.', 'success')
            return redirect(url_for('pages.home'))

        flash('E-mail ou senha inválidos.', 'danger')

    return render_template('auth/login.html')


@bp.post('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada.', 'info')
    return redirect(url_for('auth.login'))
