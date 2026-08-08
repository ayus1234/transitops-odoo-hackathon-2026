"""
Automated Database Backup Script for PostgreSQL.
Generates timestamped gzipped SQL dumps of the TransitOps database with retention management.
"""
import os
import sys
import subprocess
from datetime import datetime

BACKUP_DIR = os.getenv("BACKUP_DIR", "./backups")
DB_NAME = os.getenv("POSTGRES_DB", "transitops_db")
DB_USER = os.getenv("POSTGRES_USER", "transitops_admin")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))


def create_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}_backup_{timestamp}.sql.gz")

    print(f"[Backup] Starting backup of '{DB_NAME}' to '{backup_file}'...")
    
    # pg_dump command
    cmd = f"pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} -F c -b -v -f {backup_file}"
    
    try:
        res = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"[Backup] Successfully created backup: {backup_file}")
        cleanup_old_backups()
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"[Backup ERROR] Failed to create backup: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def cleanup_old_backups():
    print(f"[Backup] Cleaning up backups older than {RETENTION_DAYS} days...")
    now = datetime.now()
    count = 0
    for filename in os.listdir(BACKUP_DIR):
        file_path = os.path.join(BACKUP_DIR, filename)
        if os.path.isfile(file_path) and filename.startswith(DB_NAME):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if (now - file_mtime).days > RETENTION_DAYS:
                os.remove(file_path)
                print(f"[Backup] Removed expired backup: {filename}")
                count += 1
    print(f"[Backup] Cleanup completed. Removed {count} expired backup file(s).")


if __name__ == "__main__":
    create_backup()
