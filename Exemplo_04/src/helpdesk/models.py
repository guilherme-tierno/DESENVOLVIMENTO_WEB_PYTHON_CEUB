from sqlalchemy import text
from .extensions import engine

# -----------------------------
# USERS
# -----------------------------
def list_users(limit=50):
    sql = text("""
        SELECT id, name, email, role, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        return conn.execute(sql, {"limit": limit}).mappings().all()

# -----------------------------
# TICKETS
# -----------------------------
def list_tickets(limit=50):
    sql = text("""
        SELECT
          t.id, t.title, t.status, t.priority, t.created_at,
          u.name AS customer_name, a.name AS agent_name
        FROM tickets t
        JOIN users u ON u.id = t.customer_id
        LEFT JOIN users a ON a.id = t.agent_id
        ORDER BY t.created_at DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        return conn.execute(sql, {"limit": limit}).mappings().all()

def update_ticket_status(ticket_id: int, new_status: str):
    """Atualiza o status do ticket no MySQL."""
    sql = text("UPDATE tickets SET status = :status WHERE id = :id")
    with engine.begin() as conn:
        conn.execute(sql, {"status": new_status, "id": ticket_id})

def get_ticket(ticket_id: int):
    """Busca um ticket e seus updates."""
    sql_ticket = text("""
        SELECT t.*, u.name AS customer_name, u.email AS customer_email, a.name AS agent_name
        FROM tickets t
        JOIN users u ON u.id = t.customer_id
        LEFT JOIN users a ON a.id = t.agent_id
        WHERE t.id = :id
    """)

    sql_updates = text("""
        SELECT tu.id, tu.message, tu.created_at, au.name AS author_name
        FROM ticket_updates tu
        JOIN users au ON au.id = tu.author_id
        WHERE tu.ticket_id = :id
        ORDER BY tu.created_at ASC
    """)

    with engine.connect() as conn:
        ticket = conn.execute(sql_ticket, {"id": ticket_id}).mappings().first()
        if not ticket:
            return None
        updates = conn.execute(sql_updates, {"id": ticket_id}).mappings().all()
        return {"ticket": ticket, "updates": updates}