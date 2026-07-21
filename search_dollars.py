import os

dir_path = r'c:\Users\hp\Downloads\New folder (6)\transitops-odoo-hackathon-2026\frontend\src'

for root, _, files in os.walk(dir_path):
    for f in files:
        if f.endswith('.jsx') or f.endswith('.js'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for idx, line in enumerate(lines):
                # Ignore USD in OrganizationSettings options
                if 'option value="USD"' in line or 'CAD ($)' in line or 'AUD ($)' in line:
                    continue
                if 'window.location.search' in line or 'window.history' in line:
                    continue
                # only print if $ is followed by digit or { or is isolated
                if '$' in line:
                    print(f"{f}:{idx+1}: {line.strip()}")
