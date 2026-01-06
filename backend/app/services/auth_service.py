"""
Authentication service
"""
from sqlalchemy.orm import Session
from typing import Optional
from ..models.user import User
from ..utils.security import hash_password, verify_password, create_access_token
from ..schemas.auth import Token


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, username: str, email: str, password: str, is_admin: bool = False, role: str = 'RO') -> User:
    """
    Create a new user

    Args:
        db: Database session
        username: Username
        email: Email address
        password: Plain text password (will be hashed)
        is_admin: Whether user is admin
        role: User role (RO, RW, ADMIN)

    Returns:
        Created user
    """
    hashed_pwd = hash_password(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_pwd,
        is_admin=is_admin,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username and password

    Args:
        db: Database session
        username: Username
        password: Plain text password

    Returns:
        User if authentication successful, None otherwise
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_user_token(user: User) -> Token:
    """
    Create JWT token for user

    Args:
        user: User model

    Returns:
        Token schema with access_token
    """
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "is_admin": user.is_admin,
    }
    access_token = create_access_token(data=token_data)
    return Token(access_token=access_token, token_type="bearer")


def create_admin_user_if_not_exists(db: Session, username: str, email: str, password: str) -> Optional[User]:
    """
    Create admin user if it doesn't exist (for initial setup)

    Args:
        db: Database session
        username: Admin username
        email: Admin email
        password: Admin password

    Returns:
        Created or existing admin user
    """
    existing_user = get_user_by_username(db, username)
    if existing_user:
        return existing_user

    return create_user(db, username, email, password, is_admin=True, role='ADMIN')
