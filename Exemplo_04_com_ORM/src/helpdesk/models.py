from .extensions import db
from sqlalchemy.sql import func
from sqlalchemy import Enum


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(
        Enum("customer", "agent", name="user_role"),
        nullable=False,
        default="customer"
    )
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    # Relacionamentos
    customer_tickets = db.relationship(
        "Ticket",
        foreign_keys="Ticket.customer_id",
        back_populates="customer",
        lazy=True
    )

    assigned_tickets = db.relationship(
        "Ticket",
        foreign_keys="Ticket.agent_id",
        back_populates="agent",
        lazy=True
    )

    ticket_updates = db.relationship(
        "TicketUpdate",
        foreign_keys="TicketUpdate.author_id",
        back_populates="author",
        lazy=True
    )

    def __repr__(self):
        return f"<User {self.name}>"

class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)

    status = db.Column(
        Enum("open", "in_progress", "resolved", "closed", name="ticket_status"),
        nullable=False,
        default="open"
    )

    priority = db.Column(
        Enum("low", "medium", "high", name="ticket_priority"),
        nullable=False,
        default="medium"
    )

    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relacionamentos
    customer = db.relationship(
        "User",
        foreign_keys=[customer_id],
        back_populates="customer_tickets"
    )

    agent = db.relationship(
        "User",
        foreign_keys=[agent_id],
        back_populates="assigned_tickets"
    )

    updates = db.relationship(
        "TicketUpdate",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Ticket {self.title}>"

class TicketUpdate(db.Model):
    __tablename__ = "ticket_updates"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    # Relacionamentos
    ticket = db.relationship("Ticket", back_populates="updates")
    author = db.relationship("User", back_populates="ticket_updates")

    def __repr__(self):
        return f"<TicketUpdate {self.id}>"