import requests

print("Testing Export CSV...")
try:
    # Need auth token, but we can just check if the endpoint throws 500
    # Actually wait, I need a valid token for PermissionChecker.
    # I can just log in as admin to get token.
    res = requests.post("http://localhost:8000/api/v1/auth/login", json={"email": "admin@transitops.com", "password": "adminpass123"})
    if res.status_code != 200:
        print("Login failed:", res.text)
        exit(1)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    csv_res = requests.get("http://localhost:8000/api/v1/license-compliance/export/csv", headers=headers)
    print("CSV Status:", csv_res.status_code)
    if csv_res.status_code != 200:
        print(csv_res.text)
    
    pdf_res = requests.get("http://localhost:8000/api/v1/license-compliance/export/pdf", headers=headers)
    print("PDF Status:", pdf_res.status_code)
    if pdf_res.status_code != 200:
        print(pdf_res.text)

    # Test Trips Report
    # Let's see what /reports returns for trips
    
except Exception as e:
    print("Error:", e)
