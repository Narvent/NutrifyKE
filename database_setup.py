import os
import datetime
import sqlite3
import sqlite3
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
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn, 'postgres'
        except Exception as e:
            print(f"❌ Failed to connect to Postgres: {e}")
            # Fallback not automatic here since prod should fail if DB is down
            raise e
    else:
        # SQLite Connection
        conn = sqlite3.connect(DB_NAME)
        # Enable accessing columns by name (similar to RealDictCursor)
        conn.row_factory = sqlite3.Row 
        return conn, 'sqlite'

def init_db():
    """Initializes the database table (Dual Mode)."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    # Dual Mode SQL Syntax
    if db_type == 'postgres':
        # Postgres (Neon)
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_logs (
                id SERIAL PRIMARY KEY,
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                protein_g REAL,
                fat_g REAL,
                carbs_g REAL,
                quantity_label TEXT,
                date_logged TEXT NOT NULL
            );
        ''')
    else:
        # SQLite
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                protein_g REAL,
                fat_g REAL,
                carbs_g REAL,
                quantity_label TEXT,
                date_logged TEXT NOT NULL
            );
        ''')
    
    conn.commit()
    conn.close()
    
    if db_type == 'postgres':
        print("SUCCESS: Database initialized (PostgreSQL/Neon).")
    else:
        print(f"SUCCESS: Database initialized (Local SQLite: {DB_NAME}).")

def add_log(food_name, calories, protein, fat, carbs, quantity_label):
    """Adds a new meal log."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    today = datetime.date.today().isoformat()
    
    if db_type == 'postgres':
        # Postgres placeholders are %s
        c.execute('''
            INSERT INTO daily_logs (food_name, calories, protein_g, fat_g, carbs_g, quantity_label, date_logged)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        ''', (food_name, calories, protein, fat, carbs, quantity_label, today))
        log_id = c.fetchone()[0]
    else:
        # SQLite placeholders are ?
        c.execute('''
            INSERT INTO daily_logs (food_name, calories, protein_g, fat_g, carbs_g, quantity_label, date_logged)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (food_name, calories, protein, fat, carbs, quantity_label, today))
        log_id = c.lastrowid
    
    conn.commit()
    conn.close()
    return log_id

def get_todays_logs():
    """Returns all logs for the current date."""
    conn, db_type = get_db_connection()
    
    # For Postgres, use RealDictCursor to act like sqlite3.Row
    if db_type == 'postgres':
        c = conn.cursor(cursor_factory=RealDictCursor)
        placeholders = '%s'
    else:
        c = conn.cursor()
        placeholders = '?'
    
    today = datetime.date.today().isoformat()
    
    c.execute(f'SELECT * FROM daily_logs WHERE date_logged = {placeholders} ORDER BY id DESC', (today,))
    
    if db_type == 'postgres':
        # RealDictCursor return dicts directly
        rows = c.fetchall()
        logs = [dict(row) for row in rows]
    else:
        # sqlite3.Row needs explicit conversion
        rows = c.fetchall()
        logs = [dict(row) for row in rows]
        
    conn.close()
    return logs

def delete_log(log_id):
    """Deletes a log by ID."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    placeholder = '%s' if db_type == 'postgres' else '?'
    
    c.execute(f'DELETE FROM daily_logs WHERE id = {placeholder}', (log_id,))
    
    conn.commit()
    conn.close()

def clear_todays_logs():
    """Deletes all logs for today."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    placeholder = '%s' if db_type == 'postgres' else '?'
    today = datetime.date.today().isoformat()
    
    c.execute(f'DELETE FROM daily_logs WHERE date_logged = {placeholder}', (today,))
    
    conn.commit()
    conn.close()
