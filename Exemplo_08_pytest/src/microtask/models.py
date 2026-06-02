"""Modelos ORM da aplicação.

Decisão de design: usamos `String` com validação na aplicação em vez de
`Enum` nativo do SQLAlchemy. Motivos:

1. SQLite (usado em teste) traduz Enum para CHECK constraint, que dificulta
   testar caminhos de erro de validação no nível da aplicação.
2. MySQL aceita VARCHAR sem problema.
3. A validação por @validates fica visível, testável e mensagens são claras.

Roles válidos: customer, agent, admin.
Status do ticket: open, in_progress, resolved, closed.
Prioridade do ticket: low, medium, high.
"""

from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

VALID_ROLES = {"customer", "agent", "admin"}
VALID_TICKET_STATUS = {"open", "in_progress", "resolved", "closed"}
VALID_TICKET_PRIORITY = {"low", "medium", "high"}


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=func.now()
    )

    customer_tickets = db.relationship(
        "Ticket",
        foreign_keys="Ticket.customer_id",
        back_populates="customer",
        lazy=True,
    )
    assigned_tickets = db.relationship(
        "Ticket",
        foreign_keys="Ticket.agent_id",
        back_populates="agent",
        lazy=True,
    )
    ticket_updates = db.relationship(
        "TicketUpdate",
        foreign_keys="TicketUpdate.author_id",
        back_populates="author",
        lazy=True,
    )

    # ---- Validações ----
    @validates("role")
    def _valida_role(self, _key, value):
        if value not in VALID_ROLES:
            raise ValueError(f"role inválido: {value!r}")
        return value

    @validates("email")
    def _valida_email(self, _key, value):
        if not value or "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError(f"email inválido: {value!r}")
        if value.startswith("@") or value.endswith("@"):
            raise ValueError(f"email inválido: {value!r}")
        return value.strip().lower()

    @validates("name")
    def _valida_name(self, _key, value):
        if not value or not value.strip():
            raise ValueError("name é obrigatório")
        return value.strip()

    # ---- Senha ----
    def set_password(self, password: str) -> None:
        if not password or len(password) < 4:
            raise ValueError("senha deve ter ao menos 4 caracteres")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.name}>"


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    agent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="open")
    priority = db.Column(db.String(20), nullable=False, default="medium")
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=func.now()
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    customer = db.relationship(
        "User",
        foreign_keys=[customer_id],
        back_populates="customer_tickets",
    )
    agent = db.relationship(
        "User",
        foreign_keys=[agent_id],
        back_populates="assigned_tickets",
    )
    updates = db.relationship(
        "TicketUpdate",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy=True,
    )

    @validates("status")
    def _valida_status(self, _key, value):
        if value not in VALID_TICKET_STATUS:
            raise ValueError(f"status inválido: {value!r}")
        return value

    @validates("priority")
    def _valida_priority(self, _key, value):
        if value not in VALID_TICKET_PRIORITY:
            raise ValueError(f"priority inválida: {value!r}")
        return value

    @validates("title")
    def _valida_title(self, _key, value):
        if not value or len(value.strip()) < 3:
            raise ValueError("title deve ter ao menos 3 caracteres")
        return value.strip()

    def __repr__(self):
        return f"<Ticket {self.id} {self.title!r}>"


class TicketUpdate(db.Model):
    __tablename__ = "ticket_updates"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer, db.ForeignKey("tickets.id"), nullable=False
    )
    author_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=func.now()
    )

    ticket = db.relationship("Ticket", back_populates="updates")
    author = db.relationship("User", back_populates="ticket_updates")

    def __repr__(self):
        return f"<TicketUpdate {self.id}>"
