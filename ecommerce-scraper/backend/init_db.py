"""
Database Initialization Script
"""

from db import engine, SessionLocal
from models import Base, User, UserRole
from auth.security import SecurityUtils


def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")


def create_admin(email="admin@offerzone.com", password="Admin@123"):
    """Create admin user"""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"ℹ️ Admin exists: {email}")
            return
        
        admin = User(
            name="Administrator",
            email=email,
            hashed_password=SecurityUtils.hash_password(password),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"✅ Admin created: {email} / {password}")
    finally:
        db.close()


def create_user(email="user@offerzone.com", password="User@123"):
    """Create test user"""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"ℹ️ User exists: {email}")
            return
        
        user = User(
            name="Test User",
            email=email,
            hashed_password=SecurityUtils.hash_password(password),
            role=UserRole.USER,
            is_active=True
        )
        db.add(user)
        db.commit()
        print(f"✅ User created: {email} / {password}")
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🚀 Initializing Database...")
    create_tables()
    create_admin()
    create_user()
    print("\n✅ Done!\n")