import sqlite3
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from jose import JWTError

# Import from our other modules
from auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from auth.database import (
    insert_user,
    get_user_by_email,
    get_user_by_id,
    update_refresh_token
)

# =========================
# REGISTRATION
# =========================

def register_user(
    conn: sqlite3.Connection,
    email: str,
    password: str,
    learning_style: str = "patient_mentor",
    level: str = "A2"
) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Register a new user.
    
    Args:
        conn: Database connection
        email: User's email
        password: Plain text password (will be hashed)
        learning_style: Preferred tutor personality
        level: Current French level
        
    Returns:
        Tuple of (success, message, user_id)
        - success: True if registration successful
        - message: Success or error message
        - user_id: ID of newly created user (None if failed)
    """
    # Validate email format (basic check)
    if not email or "@" not in email:
        return False, "Invalid email format", None
    
    # Validate password strength
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters", None
    
    # Check if user already exists
    existing_user = get_user_by_email(conn, email)
    if existing_user:
        return False, "Email already registered", None
    
    # Hash the password
    password_hash = hash_password(password)
    
    # Insert user into database
    user_id = insert_user(conn, email, password_hash, learning_style, level)
    
    if user_id:
        return True, "Registration successful", user_id
    else:
        return False, "Registration failed. Please try again.", None

# =========================
# LOGIN
# =========================

def login_user(
    conn: sqlite3.Connection,
    email: str,
    password: str
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Authenticate a user and generate tokens.
    
    Args:
        conn: Database connection
        email: User's email
        password: Plain text password
        
    Returns:
        Tuple of (success, message, tokens)
        - success: True if login successful
        - message: Success or error message
        - tokens: Dictionary with access_token, refresh_token, and user_info
                 (None if login failed)
    """
    # Get user from database
    user = get_user_by_email(conn, email)
    
    if not user:
        return False, "Invalid email or password", None
    
    # Verify password
    if not verify_password(password, user['password_hash']):
        return False, "Invalid email or password", None
    
    # Create tokens
    token_data = {"sub": user['id']}  # "sub" is the standard JWT claim for user ID
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Store refresh token in database
    update_refresh_token(conn, user['id'], refresh_token)
    
    # Prepare response
    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_info": {
            "id": user['id'],
            "email": user['email'],
            "learning_style": user['learning_style'],
            "level": user['level']
        }
    }
    
    return True, "Login successful", tokens

# =========================
# TOKEN REFRESH
# =========================

def refresh_access_token(
    conn: sqlite3.Connection,
    refresh_token: str
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Generate a new access token using a refresh token.
    
    Args:
        conn: Database connection
        refresh_token: The refresh token
        
    Returns:
        Tuple of (success, message, new_access_token)
        - success: True if refresh successful
        - message: Success or error message
        - new_access_token: New access token (None if failed)
    """
    try:
        # Decode the refresh token
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            return False, "Invalid token", None
        
        # Get user from database
        user = get_user_by_id(conn, user_id)
        
        if not user:
            return False, "User not found", None
        
        # Verify that this refresh token matches the one in the database
        if user['refresh_token'] != refresh_token:
            return False, "Invalid or expired refresh token", None
        
        # Create new access token
        new_access_token = create_access_token({"sub": user_id})
        
        return True, "Token refreshed", new_access_token
        
    except JWTError as e:
        return False, f"Token error: {str(e)}", None
    except Exception as e:
        return False, f"Error refreshing token: {str(e)}", None

# =========================
# TOKEN VALIDATION
# =========================

def verify_access_token(
    conn: sqlite3.Connection,
    access_token: str
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Verify an access token and return user info.
    
    Args:
        conn: Database connection
        access_token: The access token to verify
        
    Returns:
        Tuple of (valid, user_info)
        - valid: True if token is valid
        - user_info: User information dictionary (None if invalid)
    """
    try:
        # Decode the token
        payload = decode_token(access_token)
        user_id = payload.get("sub")
        
        if not user_id:
            return False, None
        
        # Get user from database
        user = get_user_by_id(conn, user_id)
        
        if not user:
            return False, None
        
        # Return user info (excluding sensitive data)
        user_info = {
            "id": user['id'],
            "email": user['email'],
            "learning_style": user['learning_style'],
            "level": user['level']
        }
        
        return True, user_info
        
    except JWTError:
        return False, None
    except Exception:
        return False, None

# =========================
# LOGOUT
# =========================

def logout_user(
    conn: sqlite3.Connection,
    user_id: int
) -> bool:
    """
    Log out a user by invalidating their refresh token.
    
    Args:
        conn: Database connection
        user_id: User's ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Clear the refresh token from database
        return update_refresh_token(conn, user_id, None)
    except Exception as e:
        print(f"Error during logout: {e}")
        return False

# =========================
# HELPER FUNCTIONS
# =========================

def get_current_user(
    conn: sqlite3.Connection,
    access_token: str
) -> Optional[Dict[str, Any]]:
    """
    Get the current user from an access token.
    
    This is a convenience function that combines token verification
    and user retrieval.
    
    Args:
        conn: Database connection
        access_token: The access token
        
    Returns:
        User info dictionary if valid, None otherwise
    """
    valid, user_info = verify_access_token(conn, access_token)
    
    if valid:
        return user_info
    return None

def update_user_learning_style(
    conn: sqlite3.Connection,
    user_id: int,
    new_style: str
) -> bool:
    """
    Update a user's learning style preference.
    
    Args:
        conn: Database connection
        user_id: User's ID
        new_style: New learning style
        
    Returns:
        True if successful, False otherwise
    """
    update_sql = """
    UPDATE users
    SET learning_style = ?
    WHERE id = ?
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(update_sql, (new_style, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating learning style: {e}")
        return False

# =========================
# PASSWORD RESET (for future)
# =========================

def change_password(
    conn: sqlite3.Connection,
    user_id: int,
    old_password: str,
    new_password: str
) -> Tuple[bool, str]:
    """
    Change a user's password.
    
    Args:
        conn: Database connection
        user_id: User's ID
        old_password: Current password (plain text)
        new_password: New password (plain text)
        
    Returns:
        Tuple of (success, message)
    """
    # Get user
    user = get_user_by_id(conn, user_id)
    
    if not user:
        return False, "User not found"
    
    # Verify old password
    if not verify_password(old_password, user['password_hash']):
        return False, "Current password is incorrect"
    
    # Validate new password
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters"
    
    # Hash new password
    new_password_hash = hash_password(new_password)
    
    # Update in database
    update_sql = """
    UPDATE users
    SET password_hash = ?
    WHERE id = ?
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(update_sql, (new_password_hash, user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            # Invalidate refresh token for security
            update_refresh_token(conn, user_id, None)
            return True, "Password changed successfully. Please log in again."
        else:
            return False, "Failed to update password"
            
    except sqlite3.Error as e:
        return False, f"Error changing password: {str(e)}"
