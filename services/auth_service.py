from typing import Optional
from sqlalchemy.orm import Session
from models.user import User
from utils.auth import verify_password, get_password_hash, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta
from typing import Optional


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(self, username: str, password: str) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Create new user
        hashed_password = get_password_hash(password)
        user = User(username=username, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_access_token_for_user(self, user: User) -> str:
        """Create an access token for a user."""
        access_token_expires = timedelta(days=365)  # 1 year (effectively no timeout)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return access_token
