from flask import render_template
from . import bp
from ...models import list_users

@bp.get("/")
def lista():
    users = list_users(limit=50)
    return render_template("users/lista.html", users=users)