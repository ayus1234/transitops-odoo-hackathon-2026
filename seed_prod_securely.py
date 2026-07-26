import os
import shutil
import subprocess

root_dir = os.path.dirname(os.path.abspath(__file__))
env_prod_path = os.path.join(root_dir, '.env.production')
backend_env_path = os.path.join(root_dir, 'backend', '.env')
backend_env_backup = os.path.join(root_dir, 'backend', '.env.backup')

if not os.path.exists(env_prod_path):
    print("Error: .env.production not found!")
    exit(1)

# Check if it has DATABASE_URL
has_db = False
with open(env_prod_path, 'r', encoding='utf-8') as f:
    for line in f:
        if 'DATABASE_URL' in line:
            has_db = True
            break

if not has_db:
    print("Warning: DATABASE_URL not found in .env.production!")
    print("You may need to run: npx vercel env pull .env.production --environment=production")
    exit(1)

print("DATABASE_URL found. Proceeding with database seeding...")

# Backup local .env
if os.path.exists(backend_env_path):
    shutil.copy(backend_env_path, backend_env_backup)
    print("Backed up local .env")

# Copy production env to backend
shutil.copy(env_prod_path, backend_env_path)

try:
    print("\n--- Running init_db.py ---")
    res1 = subprocess.run(['python', 'init_db.py'], cwd=os.path.join(root_dir, 'backend'), capture_output=True, text=True)
    print(res1.stdout)
    if res1.returncode != 0:
        print("Error in init_db:", res1.stderr)
        
    print("\n--- Running seed_demo_data.py ---")
    res2 = subprocess.run(['python', 'seed_demo_data.py'], cwd=os.path.join(root_dir, 'backend'), capture_output=True, text=True)
    print(res2.stdout)
    if res2.returncode != 0:
        print("Error in seed_demo_data:", res2.stderr)

finally:
    # Restore local .env
    if os.path.exists(backend_env_backup):
        shutil.copy(backend_env_backup, backend_env_path)
        os.remove(backend_env_backup)
        print("\nRestored local .env")
    else:
        os.remove(backend_env_path)
