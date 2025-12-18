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
    """Initializes the database table (Dual Mode) and handles migrations."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    # helper to check column existence (basic migration)
    def add_column_if_not_exists(table, column, definition):
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            conn.commit()
            print(f"MIGRATION: Added {column} to {table}")
        except Exception:
            # Column likely exists
            conn.rollback()
            pass

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
                date_logged TEXT NOT NULL,
                timestamp TEXT
            );
        ''')
        # Check migration for existing tables
        add_column_if_not_exists("daily_logs", "timestamp", "TEXT")
        add_column_if_not_exists("daily_logs", "quantity_label", "TEXT")
        add_column_if_not_exists("daily_logs", "protein_g", "REAL")
        add_column_if_not_exists("daily_logs", "fat_g", "REAL")
        add_column_if_not_exists("daily_logs", "carbs_g", "REAL")
        
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
                date_logged TEXT NOT NULL,
                timestamp TEXT
            );
        ''')
        # Check migration for existing tables
        try:
            # SQLite doesn't support IF NOT EXISTS in ALTER TABLE easily, so we try/except
            c.execute("ALTER TABLE daily_logs ADD COLUMN timestamp TEXT")
            print("MIGRATION: Added timestamp to daily_logs (SQLite)")
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Helper for SQLite migrations
        def add_sqlite_column(col, defn):
            try:
                c.execute(f"ALTER TABLE daily_logs ADD COLUMN {col} {defn}")
                print(f"MIGRATION: Added {col} to daily_logs (SQLite)")
            except sqlite3.OperationalError:
                pass
        
        add_sqlite_column("quantity_label", "TEXT")
        add_sqlite_column("protein_g", "REAL")
        add_sqlite_column("fat_g", "REAL")
        add_sqlite_column("carbs_g", "REAL")
    
    conn.commit()
    conn.close()
    
    if db_type == 'postgres':
        print("SUCCESS: Database initialized (PostgreSQL/Neon).")
    else:
        print(f"SUCCESS: Database initialized (Local SQLite: {DB_NAME}).")

def add_log(food_name, calories, protein, fat, carbs, quantity_label, timestamp_iso=None):
    """Adds a new meal log."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    today = datetime.date.today().isoformat()
    # Use client timestamp if provided, else current UTC equivalent
    if timestamp_iso:
        now_ts = timestamp_iso
    else:
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if db_type == 'postgres':
        # Postgres placeholders are %s
        c.execute('''
            INSERT INTO daily_logs (food_name, calories, protein_g, fat_g, carbs_g, quantity_label, date_logged, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        ''', (food_name, calories, protein, fat, carbs, quantity_label, today, now_ts))
        log_id = c.fetchone()[0]
    else:
        # SQLite placeholders are ?
        c.execute('''
            INSERT INTO daily_logs (food_name, calories, protein_g, fat_g, carbs_g, quantity_label, date_logged, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (food_name, calories, protein, fat, carbs, quantity_label, today, now_ts))
        log_id = c.lastrowid
    
    conn.commit()
    conn.close()
    return log_id

def get_logs(date_str=None):
    """Returns logs for a specific date (default: today)."""
    conn, db_type = get_db_connection()
    
    # Default to today if no date provided
    if not date_str:
        date_str = datetime.date.today().isoformat()
    
    # For Postgres, use RealDictCursor to act like sqlite3.Row
    if db_type == 'postgres':
        c = conn.cursor(cursor_factory=RealDictCursor)
        placeholders = '%s'
    else:
        c = conn.cursor()
        placeholders = '?'
    
    # Sort by timestamp desc, fallback to id desc
    c.execute(f'SELECT * FROM daily_logs WHERE date_logged = {placeholders} ORDER BY id DESC', (date_str,))
    
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

def clear_logs(date_str=None):
    """Deletes all logs for a specific date (default: today)."""
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    if not date_str:
        date_str = datetime.date.today().isoformat()
    
    placeholder = '%s' if db_type == 'postgres' else '?'
    
    c.execute(f'DELETE FROM daily_logs WHERE date_logged = {placeholder}', (date_str,))
    
    conn.commit()
    conn.close()
