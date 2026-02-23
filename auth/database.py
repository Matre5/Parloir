import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any

# =========================
# DATABASE CONNECTION
# =========================

def create_connection(db_file: str = "database.db") -> sqlite3.Connection:
    """
    Create a database connection to SQLite database.
    
    Args:
        db_file: Path to the database file
        
    Returns:
        Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# =========================
# TABLE CREATION
# =========================

def create_users_table(conn: sqlite3.Connection) -> None:
    """
    Create the users table if it doesn't exist.
    
    Table schema:
    - id: Primary key (auto-increment)
    - email: Unique email address
    - password_hash: Hashed password
    - learning_style: User's preferred learning style (e.g., "patient_mentor")
    - level: Current French level (e.g., "A2")
    - refresh_token: Stored refresh token for session management
    - created_at: Timestamp when user was created
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        learning_style TEXT DEFAULT 'patient_mentor',
        level TEXT DEFAULT 'A2',
        refresh_token TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        print("Users table created successfully")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

# =========================
# USER OPERATIONS
# =========================

def insert_user(
    conn: sqlite3.Connection,
    email: str,
    password_hash: str,
    learning_style: str = "patient_mentor",
    level: str = "A2"
) -> Optional[int]:
    """
    Insert a new user into the database.
    
    Args:
        conn: Database connection
        email: User's email
        password_hash: Hashed password (from security.py)
        learning_style: Preferred tutor personality
        level: Current French level
        
    Returns:
        User ID if successful, None otherwise
    """
    insert_sql = """
    INSERT INTO users (email, password_hash, learning_style, level)
    VALUES (?, ?, ?, ?)
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(insert_sql, (email, password_hash, learning_style, level))
        conn.commit()
        return cursor.lastrowid  # Returns the ID of the newly created user
    except sqlite3.IntegrityError:
        print(f"Error: Email {email} already exists")
        return None
    except sqlite3.Error as e:
        print(f"Error inserting user: {e}")
        return None

def get_user_by_email(conn: sqlite3.Connection, email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by their email address.
    
    Args:
        conn: Database connection
        email: User's email
        
    Returns:
        Dictionary with user data if found, None otherwise
    """
    select_sql = """
    SELECT id, email, password_hash, learning_style, level, refresh_token, created_at
    FROM users
    WHERE email = ?
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(select_sql, (email,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)  # Convert sqlite3.Row to dictionary
        return None
    except sqlite3.Error as e:
        print(f"Error fetching user: {e}")
        return None

def get_user_by_id(conn: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by their ID.
    
    Args:
        conn: Database connection
        user_id: User's ID
        
    Returns:
        Dictionary with user data if found, None otherwise
    """
    select_sql = """
    SELECT id, email, password_hash, learning_style, level, refresh_token, created_at
    FROM users
    WHERE id = ?
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(select_sql, (user_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    except sqlite3.Error as e:
        print(f"Error fetching user: {e}")
        return None

def update_refresh_token(
    conn: sqlite3.Connection,
    user_id: int,
    refresh_token: str
) -> bool:
    """
    Update a user's refresh token.
    
    This is called after login to store the refresh token.
    
    Args:
        conn: Database connection
        user_id: User's ID
        refresh_token: New refresh token to store
        
    Returns:
        True if successful, False otherwise
    """
    update_sql = """
    UPDATE users
    SET refresh_token = ?
    WHERE id = ?
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(update_sql, (refresh_token, user_id))
        conn.commit()
        return cursor.rowcount > 0  # Returns True if a row was updated
    except sqlite3.Error as e:
        print(f"Error updating refresh token: {e}")
        return False

def update_user_level(
    conn: sqlite3.Connection,
    user_id: int,
    new_level: str
) -> bool:
    """
    Update a user's French level.
    
    This will be useful later when tracking progress.
    
    Args:
        conn: Database connection
        user_id: User's ID
        new_level: New French level (e.g., "B1")
        
    Returns:
        True if successful, False otherwise
    """
    update_sql = """
    UPDATE users
    SET level = ?
    WHERE id = ?
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(update_sql, (new_level, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating user level: {e}")
        return False

# =========================
# INITIALIZATION
# =========================

def initialize_database(db_file: str = "database.db") -> sqlite3.Connection:
    """
    Initialize the database: create connection and tables.
    
    This is the function you'll call when your app starts.
    
    Args:
        db_file: Path to the database file
        
    Returns:
        Database connection
    """
    conn = create_connection(db_file)
    if conn:
        create_users_table(conn)
        return conn
    else:
        raise Exception("Failed to create database connection")

# =========================
# UTILITY FUNCTIONS
# =========================

def close_connection(conn: sqlite3.Connection) -> None:
    """
    Close the database connection.
    
    Args:
        conn: Database connection to close
    """
    if conn:
        conn.close()
        print("Database connection closed")
