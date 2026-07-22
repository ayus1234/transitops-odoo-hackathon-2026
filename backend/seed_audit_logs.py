import os
import sys
import random
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission_audit import PermissionAuditLog

def main():
    db = SessionLocal()
    try:
        # Get the master admin user
        admin = db.query(User).filter(User.email == "admin@transitops.com").first()
        admin_id = admin.id if admin else None

        # Get some roles
        unassigned_role = db.query(Role).filter(Role.name == "Unassigned").first()
        fleet_manager_role = db.query(Role).filter(Role.name == "Fleet Manager").first()
        
        # Get a sample user
        sample_user = db.query(User).filter(User.email.like("%transitops.com")).offset(2).first()

        logs = []

        now = datetime.utcnow()

        # 1. Created Unassigned Role
        if unassigned_role:
            logs.append(PermissionAuditLog(
                user_id=admin_id,
                action="CREATE_ROLE",
                module="RBAC",
                target_role_id=unassigned_role.id,
                new_value={"name": "Unassigned", "is_custom": False},
                timestamp=now - timedelta(minutes=15)
            ))

        # 2. Re-assigned roles to realistic distribution
        logs.append(PermissionAuditLog(
            user_id=admin_id,
            action="BULK_ASSIGN_ROLE",
            module="User Management",
            new_value={"users_affected": 50, "status": "Success"},
            timestamp=now - timedelta(minutes=10)
        ))

        # 3. Cleaned up overlapping custom roles
        logs.append(PermissionAuditLog(
            user_id=admin_id,
            action="REMOVE_ADDITIONAL_ROLES",
            module="User Management",
            previous_value={"removed_count": 142},
            timestamp=now - timedelta(minutes=8)
        ))

        # 4. Assigned specific user
        if sample_user and fleet_manager_role:
            logs.append(PermissionAuditLog(
                user_id=admin_id,
                action="ASSIGN_ROLE",
                module="User Management",
                target_user_id=sample_user.id,
                target_role_id=fleet_manager_role.id,
                new_value={"role": "Fleet Manager"},
                timestamp=now - timedelta(minutes=5)
            ))

        # 5. Moved 3 users to Unassigned
        if unassigned_role:
            logs.append(PermissionAuditLog(
                user_id=admin_id,
                action="ASSIGN_ROLE",
                module="User Management",
                target_role_id=unassigned_role.id,
                new_value={"users_affected": 3, "role": "Unassigned"},
                timestamp=now - timedelta(minutes=2)
            ))

        # Clear existing logs for a fresh start
        db.query(PermissionAuditLog).delete()
        
        # Add new realistic logs
        for log in logs:
            db.add(log)

        db.commit()
        print("Successfully seeded realistic RBAC audit logs!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
