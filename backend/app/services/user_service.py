from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_oauth(db: Session, provider: str, oauth_id: str):
    return db.query(User).filter(
        User.oauth_provider == provider,
        User.oauth_id == oauth_id
    ).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email,
        name=user.name,
        oauth_provider=user.oauth_provider,
        oauth_id=user.oauth_id,
        role=user.role,
        verified_adult=False,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_or_create_user(db: Session, provider: str, oauth_id: str, email: str, name: str):
    user = get_user_by_oauth(db, provider, oauth_id)
    if not user:
        user_create = UserCreate(
            email=email,
            name=name,
            oauth_provider=provider,
            oauth_id=oauth_id,
            role="parent"  # Default role for new users
        )
        user = create_user(db, user_create)
    return user
