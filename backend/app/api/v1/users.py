"""
User Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...dependencies import get_current_user
from ...schemas.user import User, UserCreate, UserUpdate
from ...services import user_service
from ...models.user import User as UserModel

router = APIRouter(prefix="/users", tags=["Users"])


def require_admin(current_user: UserModel = Depends(get_current_user)):
    """Dependency to require ADMIN role"""
    if current_user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage users"
        )
    return current_user


@router.get("/", response_model=List[User])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Get list of all users (ADMIN only)

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        List of users
    """
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Get a specific user by ID (ADMIN only)

    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        User details

    Raises:
        HTTPException: If user not found
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Create a new user (ADMIN only)

    Args:
        user_data: User creation data
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        Created user

    Raises:
        HTTPException: If user with same username or email exists
    """
    # Check if user with same username exists
    existing_username = user_service.get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username '{user_data.username}' already exists"
        )

    # Check if user with same email exists
    existing_email = user_service.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user_data.email}' already exists"
        )

    try:
        user = user_service.create_user(
            db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Update a user (ADMIN only)

    Args:
        user_id: User ID
        user_data: User update data
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found or validation fails
    """
    # Check if user exists
    existing_user = user_service.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # Check if email is being changed and if it's already taken
    if user_data.email and user_data.email != existing_user.email:
        existing_email = user_service.get_user_by_email(db, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_data.email}' is already taken"
            )

    # Prevent admin from removing their own admin role
    if user_id == current_user.id and user_data.role and user_data.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own admin role"
        )

    update_data = user_data.model_dump(exclude_unset=True)
    user = user_service.update_user(db, user_id, **update_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Delete a user (ADMIN only)

    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated admin user

    Raises:
        HTTPException: If user not found or trying to delete self
    """
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )

    deleted = user_service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return None
