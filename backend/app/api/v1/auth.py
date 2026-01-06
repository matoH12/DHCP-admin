"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...database import get_db
from ...dependencies import get_current_user
from ...schemas.auth import LoginRequest, Token
from ...schemas.user import User as UserSchema
from ...services.auth_service import authenticate_user, create_user_token
from ...models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with username and password to get JWT token

    Args:
        login_data: Login credentials (username, password)
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    user = authenticate_user(db, login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_user_token(user)
    return token


@router.get("/me", response_model=UserSchema)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information

    Args:
        current_user: Current authenticated user from JWT

    Returns:
        Current user information
    """
    return current_user


@router.post("/logout")
def logout():
    """
    Logout endpoint (client-side token deletion)

    Note: Since we're using stateless JWT tokens, logout is handled client-side
    by deleting the token. This endpoint exists for API consistency.

    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
