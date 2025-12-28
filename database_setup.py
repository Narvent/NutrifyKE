import os
import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None
    print("WARNING: PostgreSQL driver not found. Running in SQLite mode.")

# --- CONFIGURATION ---
DB_NAME = "nutrify.db"
# Vercel provides this env var automatically for Neon/Postgres
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """
    Returns a database connection.
    - If DATABASE_URL is set -> Connects to PostgreSQL (Neon).
    - Else -> Connects to local SQLite.
    """
    if DATABASE_URL:
        # PostgreSQL Connection
        if psycopg2 is None:
             raise ImportError("PostgreSQL driver (psycopg2) not found, but DATABASE_URL is set. Please install 'psycopg2-binary'.")
             
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn, 'postgres'
        except Exception as e:
            print(f"❌ Failed to connect to Postgres: {e}")
            raise e
    else:
        # SQLite Connection
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row 
        return conn, 'sqlite'

def init_db():
    """Initializes the database tables (Dual Mode) and handles migrations."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    # helper to check column existence (basic migration)
    def add_column_if_not_exists(table, column, definition):
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            conn.commit()
            print(f"MIGRATION: Added {column} to {table}")
        except Exception:
            conn.rollback()
            pass

    # Dual Mode SQL Syntax
    if db_type == 'postgres':
        # Postgres (Neon)
        
        # 1. Users Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # 2. Daily Logs Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                protein_g REAL,
                fat_g REAL,
                carbs_g REAL,
                quantity_label TEXT,
                date_logged TEXT NOT NULL,
                timestamp TEXT
            );
        ''')
        
        # Migrations for existing tables
        add_column_if_not_exists("daily_logs", "timestamp", "TEXT")
        add_column_if_not_exists("daily_logs", "quantity_label", "TEXT")
        add_column_if_not_exists("daily_logs", "protein_g", "REAL")
        add_column_if_not_exists("daily_logs", "fat_g", "REAL")
        add_column_if_not_exists("daily_logs", "carbs_g", "REAL")
        add_column_if_not_exists("daily_logs", "user_id", "INTEGER REFERENCES users(id)")
        
    else:
        # SQLite
        
        # 1. Users Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # 2. Daily Logs Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                protein_g REAL,
                fat_g REAL,
                carbs_g REAL,
                quantity_label TEXT,
                date_logged TEXT NOT NULL,
                timestamp TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        ''')
        
        # SQLite Migrations
        def add_sqlite_column(col, defn):
            try:
                c.execute(f"ALTER TABLE daily_logs ADD COLUMN {col} {defn}")
                print(f"MIGRATION: Added {col} to daily_logs (SQLite)")
            except sqlite3.OperationalError:
                pass
        
        add_sqlite_column("timestamp", "TEXT")
        add_sqlite_column("quantity_label", "TEXT")
        add_sqlite_column("protein_g", "REAL")
        add_sqlite_column("fat_g", "REAL")
        add_sqlite_column("carbs_g", "REAL")
        add_sqlite_column("user_id", "INTEGER")
    
    conn.commit()
    conn.close()
    
    print(f"SUCCESS: Database initialized ({db_type}).")

# --- USER MANAGEMENT ---

def create_user(email, password):
    """Creates a new user. Returns user_id or None if email exists."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    password_hash = generate_password_hash(password)
    
    try:
        if db_type == 'postgres':
            c.execute('INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id', (email, password_hash))
            user_id = c.fetchone()[0]
        else:
            c.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
            user_id = c.lastrowid
        conn.commit()
        return user_id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    """Returns user dict or None."""
    conn, db_type = get_db_connection()
    
    if db_type == 'postgres':
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = c.fetchone()
        if user: user = dict(user)
    else:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        if user: user = dict(user)
        
    conn.close()
    return user

def get_user_by_id(user_id):
    """Returns user dict or None."""
    conn, db_type = get_db_connection()
    
    if db_type == 'postgres':
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = c.fetchone()
        if user: user = dict(user)
    else:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        if user: user = dict(user)
        
    conn.close()
    return user

# --- LOGGING FUNCTIONS (Multi-Tenant) ---

def add_log(user_id, food_name, calories, protein, fat, carbs, quantity_label, timestamp_iso=None, date_logged=None):
    """Adds a new meal log for a specific user."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    if date_logged:
        today = date_logged
    else:
        today = datetime.date.today().isoformat()
        
    if timestamp_iso:
        now_ts = timestamp_iso
    else:
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if db_type == 'postgres':
        c.execute('''
            INSERT INTO daily_logs (user_id, food_name, calories, protein_g, fat_g, carbs_g, quantity_label, date_logged, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        ''', (user_id, food_name, calories, protein, fat, carbs, quantity_label, today, now_ts))
        log_id = c.fetchone()[0]
    else:
        c.execute('''
            INSERT INTO daily_logs (user_id, food_name, calories, protein_g, fat_g, carbs_g, quantity_label, date_logged, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, food_name, calories, protein, fat, carbs, quantity_label, today, now_ts))
        log_id = c.lastrowid
    
    conn.commit()
    conn.close()
    return log_id

def get_logs(user_id, date_str=None):
    """Returns logs for a specific user and date."""
    conn, db_type = get_db_connection()
    
    if not date_str:
        date_str = datetime.date.today().isoformat()
    
    if db_type == 'postgres':
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('SELECT * FROM daily_logs WHERE user_id = %s AND date_logged = %s ORDER BY id DESC', (user_id, date_str))
        rows = c.fetchall()
        logs = [dict(row) for row in rows]
    else:
        c = conn.cursor()
        c.execute('SELECT * FROM daily_logs WHERE user_id = ? AND date_logged = ? ORDER BY id DESC', (user_id, date_str))
        rows = c.fetchall()
        logs = [dict(row) for row in rows]
        
    conn.close()
    return logs

def delete_log(log_id, user_id):
    """Deletes a log by ID, ensuring it belongs to the user."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    if db_type == 'postgres':
        c.execute('DELETE FROM daily_logs WHERE id = %s AND user_id = %s', (log_id, user_id))
    else:
        c.execute('DELETE FROM daily_logs WHERE id = ? AND user_id = ?', (log_id, user_id))
    
    conn.commit()
    conn.close()

def clear_logs(user_id, date_str=None):
    """Deletes all logs for a specific user and date."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    if not date_str:
        date_str = datetime.date.today().isoformat()
    
    if db_type == 'postgres':
        c.execute('DELETE FROM daily_logs WHERE user_id = %s AND date_logged = %s', (user_id, date_str))
    else:
        c.execute('DELETE FROM daily_logs WHERE user_id = ? AND date_logged = ?', (user_id, date_str))
    
    conn.commit()
    conn.close()
