from functools import wraps
from flask import redirect, session, current_app
from typing import Dict, List, Optional, Any
from datetime import datetime
from cs50 import SQL


def login_required(f):
    """Decorate routes to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_user_role(db: SQL, user_id: int) -> Optional[str]:
    """Get user role from database"""
    try:
        user = db.execute("SELECT role FROM users WHERE id = ?", user_id)
        return user[0]["role"] if user else None
    except Exception as e:
        current_app.logger.error(f"Error getting user role: {str(e)}")
        return None


def get_bookings(
    db: SQL,
    user_role: str,
    user_id: int,
    selected_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get bookings based on user role and selected date"""
    if not selected_date:
        selected_date = datetime.now().strftime('%Y-%m-%d')
    
    base_query = """
        SELECT 
            r.id,
            ps.slot_number,
            r.visitor_name,
            r.company,
            datetime(r.arrival_time) as arrival_time,
            datetime(r.departure_time) as departure_time,
            u.username as manager_name
        FROM reservations r
        JOIN parking_slots ps ON r.slot_id = ps.id
        JOIN users u ON r.user_id = u.id
    """
    
    try:
        if user_role == "manager":
            return db.execute(
                f"{base_query} WHERE r.user_id = ? AND DATE(r.arrival_time) = ? ORDER BY r.arrival_time ASC",
                user_id,
                selected_date
            )
        else:
            return db.execute(
                f"{base_query} WHERE DATE(r.arrival_time) = ? ORDER BY r.arrival_time ASC",
                selected_date
            )
    except Exception as e:
        current_app.logger.error(f"Error getting bookings: {str(e)}")
        return []
