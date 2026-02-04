"""
User management service.
"""
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Get user by email address.

    Args:
        db: Database session
        email: User email address

    Returns:
        User object or None
    """
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object or None
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    email: str,
    full_name: str | None = None,
    role: UserRole = UserRole.USER,
    saml_name_id: str | None = None,
    saml_session_index: str | None = None,
) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        email: User email address
        full_name: User's full name
        role: User role (default: USER)
        saml_name_id: SAML NameID
        saml_session_index: SAML session index

    Returns:
        Created User object
    """
    user = User(
        email=email.lower(),
        full_name=full_name,
        role=role,
        saml_name_id=saml_name_id,
        saml_session_index=saml_session_index,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"Created user: {email} with role {role}")
    return user


def update_user_saml_info(
    db: Session,
    user: User,
    saml_name_id: str | None = None,
    saml_session_index: str | None = None,
) -> User:
    """
    Update user's SAML information.

    Args:
        db: Database session
        user: User object
        saml_name_id: SAML NameID
        saml_session_index: SAML session index

    Returns:
        Updated User object
    """
    if saml_name_id:
        user.saml_name_id = saml_name_id
    if saml_session_index:
        user.saml_session_index = saml_session_index

    db.commit()
    db.refresh(user)
    return user


def bootstrap_admin_if_needed(db: Session, email: str, full_name: str | None = None) -> User:
    """
    Bootstrap the first admin user if this is the bootstrap admin email.

    Args:
        db: Database session
        email: User email address
        full_name: User's full name

    Returns:
        User object (either existing or newly created admin)
    """
    # Check if this is the bootstrap admin email
    is_bootstrap_admin = email.lower() == settings.bootstrap_admin_email.lower()

    # Get or create user
    user = get_user_by_email(db, email)

    if user is None:
        # User doesn't exist - create them
        role = UserRole.ADMIN if is_bootstrap_admin else UserRole.USER
        user = create_user(db, email, full_name, role)

        if is_bootstrap_admin:
            logger.info(f"Bootstrap admin user created: {email}")
    elif is_bootstrap_admin and user.role != UserRole.ADMIN:
        # User exists but isn't admin - upgrade them
        user.role = UserRole.ADMIN
        db.commit()
        db.refresh(user)
        logger.info(f"User upgraded to admin: {email}")

    return user


def count_users(db: Session) -> int:
    """
    Count total number of users.

    Args:
        db: Database session

    Returns:
        Total user count
    """
    return db.query(User).count()
