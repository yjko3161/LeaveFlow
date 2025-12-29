import requests

BASE_URL = "http://127.0.0.1:5000"
EMPLOYEE_CREDS = {'email': 'employee@flexlite.com', 'password': 'password'}
ADMIN_CREDS = {'email': 'admin@flexlite.com', 'password': 'password'}

def test_features():
    s = requests.Session()
    # Login as Employee
    r = s.post(f"{BASE_URL}/auth/login", data=EMPLOYEE_CREDS)
    if "Dashboard" not in r.text and r.url != f"{BASE_URL}/" and "/auth/login" in r.url:
         print("[FAIL] Login failed")
         return False
    print("[OK] Login successful")

    # Check Quote Links
    r = s.get(f"{BASE_URL}/quote/")
    if r.status_code == 200: print("[OK] Quote Index page accessible")
    else: print(f"[FAIL] Quote Index page {r.status_code}")

    r = s.get(f"{BASE_URL}/quote/new")
    if r.status_code == 200: print("[OK] Quote New Form page accessible")
    else: print(f"[FAIL] Quote New Form page {r.status_code}")

    # Create Quote
    data = {
        'client_name': 'Test Client',
        'title': 'Test Quote 1',
        'desc': 'Item A',
        'qty': '10',
        'price': '5000'
    }
    r = s.post(f"{BASE_URL}/quote/new", data=data)
    if "견적서가 생성" in r.text or r.status_code == 200:
        print("[OK] Quote Created")
    else:
        print(f"[FAIL] Quote Creation failed {r.status_code}")

    # Run Check Settings as Admin
    s_admin = requests.Session()
    s_admin.post(f"{BASE_URL}/auth/login", data=ADMIN_CREDS)
    r = s_admin.get(f"{BASE_URL}/leave/manage")
    if r.status_code == 200: print("[OK] Leave Manage page accessible (Admin)")
    else: print(f"[FAIL] Leave Manage page {r.status_code}")

    return True

if __name__ == "__main__":
    test_features()
