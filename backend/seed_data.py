"""
Seed script to populate initial data (roles and admin user).
Run this after creating the database and running migrations.

Usage:
    python seed_data.py
"""
import sys
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User


def seed_roles(db: Session):
    """Create default roles."""
    print("Seeding roles...")
    
    roles_data = [
        {
            "name": "Fleet Manager",
            "permissions": {
                "vehicles": ["read", "create", "update", "delete"],
                "drivers": ["read", "create", "update", "delete"],
                "trips": ["read", "create", "update", "delete"],
                "maintenance": ["read", "create", "update", "delete"],
                "fuel": ["read", "create", "update", "delete"],
                "expenses": ["read", "create", "update", "delete", "approve"],
                "reports": ["read", "export"],
                "users": ["read", "create", "update"],
            }
        },
        {
            "name": "Driver",
            "permissions": {
                "trips": ["read"],
                "fuel": ["create"],
                "profile": ["read", "update"],
            }
        },
        {
            "name": "Safety Officer",
            "permissions": {
                "drivers": ["read", "update"],
                "trips": ["read"],
                "reports": ["read"],
            }
        },
        {
            "name": "Financial Analyst",
            "permissions": {
                "expenses": ["read"],
                "fuel": ["read"],
                "maintenance": ["read"],
                "reports": ["read", "export"],
                "analytics": ["read"],
            }
        }
    ]
    
    created_roles = {}
    for role_data in roles_data:
        # Check if role already exists
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if existing_role:
            print(f"  ✓ Role '{role_data['name']}' already exists")
            created_roles[role_data["name"]] = existing_role
        else:
            role = Role(**role_data)
            db.add(role)
            db.commit()
            db.refresh(role)
            created_roles[role_data["name"]] = role
            print(f"  ✓ Created role: {role.name}")
    
    return created_roles


def seed_admin_user(db: Session, fleet_manager_role: Role):
    """Create default admin user."""
    print("\nSeeding admin user...")
    
    admin_email = "admin@transitops.com"
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if existing_admin:
        print(f"  ✓ Admin user '{admin_email}' already exists")
        return existing_admin
    
    admin_user = User(
        email=admin_email,
        password_hash=get_password_hash("admin123"),
        first_name="Admin",
        last_name="User",
        phone_number="+1234567890",
        role_id=fleet_manager_role.id,
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"  ✓ Created admin user: {admin_user.email}")
    print(f"  → Email: {admin_email}")
    print(f"  → Password: admin123")
    print(f"  → Role: Fleet Manager")
    
    return admin_user


def seed_sample_users(db: Session, roles: dict):
    """Create sample users for each role."""
    print("\nSeeding sample users...")
    
    sample_users = [
        {
            "email": "driver@transitops.com",
            "password": "driver123",
            "first_name": "Rajesh",
            "last_name": "Kumar",
            "phone_number": "+919876543210",
            "role": "Driver"
        },
        {
            "email": "safety@transitops.com",
            "password": "safety123",
            "first_name": "Priya",
            "last_name": "Sharma",
            "phone_number": "+919876543211",
            "role": "Safety Officer"
        },
        {
            "email": "finance@transitops.com",
            "password": "finance123",
            "first_name": "Amit",
            "last_name": "Patel",
            "phone_number": "+919876543212",
            "role": "Financial Analyst"
        }
    ]
    
    for user_data in sample_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"  ✓ User '{user_data['email']}' already exists")
            continue
        
        role = roles[user_data["role"]]
        user = User(
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            phone_number=user_data["phone_number"],
            role_id=role.id,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"  ✓ Created user: {user.email} ({user_data['role']})")


def main():
    """Main seed function."""
    print("=" * 60)
    print("TransitOps Database Seeding")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        
        # Seed roles
        roles = seed_roles(db)
        
        # Seed admin user
        seed_admin_user(db, roles["Fleet Manager"])
        
        # Seed sample users
        seed_sample_users(db, roles)
        
        print("\n" + "=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
        print("\nDefault credentials:")
        print("  Admin:")
        print("    Email: admin@transitops.com")
        print("    Password: admin123")
        print("\n  Driver:")
        print("    Email: driver@transitops.com")
        print("    Password: driver123")
        print("\n  Safety Officer:")
        print("    Email: safety@transitops.com")
        print("    Password: safety123")
        print("\n  Financial Analyst:")
        print("    Email: finance@transitops.com")
        print("    Password: finance123")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {str(e)}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
