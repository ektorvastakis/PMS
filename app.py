# Standard library imports
import os
from datetime import datetime, timedelta

# Third-party imports
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Local imports
from config import config
from helpers import login_required, get_user_role, get_bookings


# App initialization and configuration
def create_app():
    app = Flask(__name__)
    
    # Load environment variables
    load_dotenv()
    
    # App configurations
    app.config.from_object(config[os.environ.get('FLASK_ENV', 'default')])
    
    # Initialize Flask-Session
    Session(app)
    
    # Configure logging
    setup_logging(app)
    
    return app

def setup_logging(app):
    if not app.debug:
        handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

# Create app instance
app = create_app()

# Database configuration
db = SQL("sqlite:///parking_slots.db")

# roles
VALID_ROLES = ['manager', 'lobby', 'guard']

# Unified error handling
class AppError(Exception):
    """Base error class for application"""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code

@app.errorhandler(AppError)
@app.errorhandler(Exception)
def handle_error(error):
    """Unified error handler for all exceptions"""
    if isinstance(error, AppError):
        status_code = error.status_code
        message = error.message
    else:
        status_code = 500
        message = "An unexpected error occurred"
        app.logger.error(f"Unhandled error: {str(error)}")

    if request.is_json:
        return jsonify({"error": message}), status_code
    
    return render_template("error.html", error=message), status_code

@app.errorhandler(404)
def not_found_error(error):
    return render_template('apology.html', 
                         message="Page not found", 
                         top="404", 
                         bottom="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('apology.html', 
                         message="Internal server error", 
                         top="500", 
                         bottom="Something went wrong"), 500

# Database initialization
def init_db():
    """Initialize database tables"""
    tables = {
        'users': """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """,
        'parking_slots': """
            CREATE TABLE IF NOT EXISTS parking_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_number TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'available'
            )
        """,
        'reservations': """
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                slot_id INTEGER NOT NULL,
                visitor_name TEXT NOT NULL,
                company TEXT NOT NULL,
                arrival_time DATETIME NOT NULL,
                departure_time DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (slot_id) REFERENCES parking_slots(id)
            )
        """
    }
    
    for table_name, query in tables.items():
        try:
            db.execute(query)
        except Exception as e:
            raise AppError(f"Failed to create {table_name} table: {str(e)}")

# Initialize database on startup
try:
    init_db()
except Exception as e:
    app.logger.error(f'Database initialization failed: {str(e)}')
    raise

@app.route("/settings", methods=["GET", "POST"])
def settings():
    """Handle system and user settings"""
    user_id = session.get("user_id")
    logged_in = user_id is not None

    if request.method == "POST":
        if not logged_in:
            # System settings (no user logged in)
            if "set_slots" in request.form:
                num_slots = int(request.form.get("num_slots", 0))
                if num_slots < 1:
                    raise AppError("Invalid number of slots", 400)
                
                db.execute("DELETE FROM parking_slots")
                for i in range(1, num_slots + 1):
                    db.execute(
                        "INSERT INTO parking_slots (slot_number, status) VALUES (?, ?)",
                        f"P{i:02d}", "available"
                    )
                flash("Parking slots updated successfully!")
            
            elif "delete_users" in request.form:
                db.execute("DELETE FROM reservations")
                db.execute("DELETE FROM users")
                flash("All users and data deleted successfully!")
        else:
            # User settings (logged in)
            if "delete_account" in request.form:
                db.execute("DELETE FROM reservations WHERE user_id = ?", user_id)
                db.execute("DELETE FROM users WHERE id = ?", user_id)
                session.clear()
                flash("Account deleted successfully!")
                return redirect("/")

    current_slots = db.execute("SELECT COUNT(*) as count FROM parking_slots")[0]["count"]
    user_count = db.execute("SELECT COUNT(*) as count FROM users")[0]["count"]

    return render_template(
        "settings.html",
        logged_in=logged_in,
        current_slots=current_slots,
        user_count=user_count
    )

@app.route("/")
def index():
    """Show landing page or redirect to dashboard if logged in"""
    if session.get("user_id"):
        return redirect("/dashboard")
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            raise AppError("Must provide username and password", 400)

        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not user or not check_password_hash(user[0]["hash"], password):
            raise AppError("Invalid username and/or password", 403)

        session["user_id"] = user[0]["id"]
        flash("Logged in successfully!")
        return redirect("/dashboard")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        role = request.form.get("role")

        if not username or not password or not confirmation or not role:
            raise AppError("All fields are required", 400)

        if password != confirmation:
            raise AppError("Passwords do not match", 400)

        if role not in VALID_ROLES:
            raise AppError("Invalid role selected", 400)

        try:
            hash = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (username, hash, role) VALUES (?, ?, ?)",
                username, hash, role
            )
            flash("Registered successfully!")
            return redirect("/login")
        except Exception:
            raise AppError("Username already exists", 400)

    return render_template("register.html", roles=VALID_ROLES)

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("Logged out successfully!")
    return redirect("/")

@app.route("/dashboard")
@login_required
def dashboard():
    """Show dashboard based on user role"""
    user_id = session["user_id"]
    user_role = get_user_role(db, user_id)
    
    if not user_role:
        raise AppError("User role not found", 400)

    selected_date = request.args.get("date", datetime.now().strftime('%Y-%m-%d'))
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    bookings = get_bookings(db, user_role, user_id, selected_date)

    return render_template(
        "staff_dashboard.html",
        user_role=user_role,
        bookings=bookings,
        current_time=current_time,
        selected_date=selected_date
    )

@app.route("/get_available_slot")
@login_required
def get_available_slot():
    """Check slot availability for given time period"""
    arrival = request.args.get("arrival")
    departure = request.args.get("departure")
    
    if not arrival or not departure:
        return jsonify({"available": False})
    
    # Find available slot
    available_slot = db.execute("""
        SELECT ps.id, ps.slot_number
        FROM parking_slots ps
        WHERE ps.id NOT IN (
            SELECT slot_id 
            FROM reservations 
            WHERE (arrival_time <= ? AND departure_time >= ?)
        )
        LIMIT 1
    """, departure, arrival)
    
    if available_slot:
        return jsonify({
            "available": True,
            "slot_id": available_slot[0]["id"],
            "slot_number": available_slot[0]["slot_number"]
        })
    
    return jsonify({"available": False})

@app.route("/reserve", methods=["GET", "POST"])
@login_required
def reserve():
    """Handle parking slot reservations"""
    if request.method == "POST":
        slot_id = request.form.get("slot_id")
        visitor_name = request.form.get("visitor_name")
        company = request.form.get("company")
        arrival_time = request.form.get("arrival_time")
        departure_time = request.form.get("departure_time")
        
        if not all([slot_id, visitor_name, company, arrival_time, departure_time]):
            raise AppError("All fields are required", 400)
        
        db.execute("""
            INSERT INTO reservations 
            (user_id, slot_id, visitor_name, company, arrival_time, departure_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, session["user_id"], slot_id, visitor_name, company, arrival_time, departure_time)
        
        flash("Reservation successful!")
        return redirect("/dashboard")
    
    return render_template(
        "reserve.html",
        current_time=datetime.now().strftime('%Y-%m-%dT%H:%M')
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

