"""
User service for CRUD operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.user import User
from ..utils.security import hash_password


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users"""
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: str = 'RO',
    is_active: bool = True
) -> User:
    """
    Create a new user

    Args:
        db: Database session
        username: Username
        email: Email address
        password: Plain text password
        role: User role (RO, RW, ADMIN)
        is_active: Whether user is active

    Returns:
        Created user
    """
    hashed_password = hash_password(password)
    is_admin = (role == 'ADMIN')

    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role,
        is_active=is_active,
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session,
    user_id: int,
    **kwargs
) -> Optional[User]:
    """
    Update a user

    Args:
        db: Database session
        user_id: User ID
        **kwargs: Fields to update

    Returns:
        Updated user or None if not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    # Handle password separately
    if 'password' in kwargs and kwargs['password']:
        kwargs['hashed_password'] = hash_password(kwargs['password'])
        del kwargs['password']

    # Update is_admin based on role
    if 'role' in kwargs:
        kwargs['is_admin'] = (kwargs['role'] == 'ADMIN')

    for key, value in kwargs.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if deleted, False if not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True
