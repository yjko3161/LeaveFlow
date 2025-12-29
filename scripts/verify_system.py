import requests
import sys
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"
EMPLOYEE_CREDS = {'email': 'employee@flexlite.com', 'password': 'password'}
MANAGER_CREDS = {'email': 'manager@flexlite.com', 'password': 'password'}
ADMIN_CREDS = {'email': 'admin@flexlite.com', 'password': 'password'}

def get_csrf_token(session, url):
    # If CSRF protection is enabled in future
    return None

def login(session, email, password):
    r = session.post(f"{BASE_URL}/auth/login", data={'email': email, 'password': password})
    if r.url == f"{BASE_URL}/":
        print(f"[OK] Login successful as {email}")
        return True
    print(f"[FAIL] Login failed for {email}. URL: {r.url}")
    # Simple check for flash message in HTML
    if "이메일 또는 비밀번호가 올바르지 않습니다" in r.text:
        print("Reason: Invalid Credentials")
    else:
        print("Reason: Unknown (possibly CSRF or Form Error)")
    return False

def test_leave_flow():
    print("\n--- Testing Leave Flow ---")
    s = requests.Session()
    if not login(s, **EMPLOYEE_CREDS): return False
    
    # 1. Create Request
    data = {
        'leave_type': 'ANNUAL',
        'start_date': '2025-05-01',
        'end_date': '2025-05-03',
        'reason': 'Auto Test Leave'
    }
    r = s.post(f"{BASE_URL}/leave/new", data=data)
    if "연차 신청이 완료되었습니다" in r.text or r.status_code == 200:
        print("[OK] Leave Request Submitted")
    else:
        print(f"[FAIL] Leave Submit Failed: {r.status_code}")
        return False
        
    s.close()
    
    # 2. Approve (Manager)
    s = requests.Session()
    if not login(s, **MANAGER_CREDS): return False
    
    # Check Inbox
    r = s.get(f"{BASE_URL}/approval/inbox")
    soup = BeautifulSoup(r.text, 'html.parser')
    # Find link to detail with text "LEAVE"
    links = soup.find_all('a', href=True)
    target_link = None
    for l in links:
        if "/approval/" in l['href'] and "LEAVE" in l.text:
            target_link = l['href']
            break
            
    if target_link:
        req_id = target_link.split('/')[-1]
        print(f"[OK] Found Pending Leave Request ID: {req_id}")
        
        # Action Approve
        r = s.post(f"{BASE_URL}/approval/{req_id}/action", data={'action': 'APPROVE', 'comment': 'Auto Approved'})
        if "성공적으로 처리되었습니다" in r.text:
             print("[OK] Leave Request Approved")
        else:
             print("[FAIL] Approval Failed")
             return False
    else:
        print("[FAIL] No Pending Leave Request found in Inbox")
        return False
        
    return True

def test_expense_flow():
    print("\n--- Testing Expense Flow ---")
    s = requests.Session()
    if not login(s, **EMPLOYEE_CREDS): return False
    
    # 1. Add Receipt
    # Need category ID. Assuming 1 from seed.
    data = {
        'usage_date': '2025-04-01',
        'merchant': 'Test Cafe',
        'amount': '15000',
        'category_id': '1',
        'description': 'Team Coffee'
    }
    # Create a dummy file
    files = {'receipt_file': ('receipt.txt', 'dummy content')}
    r = s.post(f"{BASE_URL}/expense/receipt/new", data=data, files=files)
    if "영수증이 등록되었습니다" in r.text:
         print("[OK] Receipt Added")
    else:
         print(f"[FAIL] Receipt Add Failed. URL: {r.url}")
         # print(r.text) # Too verbose, maybe just title or flash
         soup = BeautifulSoup(r.text, 'html.parser')
         flash = soup.find('div', class_='text-red-800') # Error flash usually red
         if flash: print(f"Flash Error: {flash.text.strip()}")
         else: print("No error flash found.")
         return False

    # Get Receipt ID (from list page parser or assumption)
    # The list page is rendered at /expense/
    r = s.get(f"{BASE_URL}/expense/")
    soup = BeautifulSoup(r.text, 'html.parser')
    checkbox = soup.find('input', {'name': 'receipt_ids'})
    if not checkbox:
        print("[FAIL] No receipt checkbox found")
        return False
        
    receipt_id = checkbox['value']
    
    # 2. Submit Report
    data = {
        'title': 'April Expenses',
        'receipt_ids': [receipt_id]
    }
    r = s.post(f"{BASE_URL}/expense/report/new", data=data)
    if "지출결의서가 제출되었습니다" in r.text:
         print("[OK] Expense Report Submitted")
    else:
         print("[FAIL] Expense Report Submit Failed")
         return False
         
    s.close()
    
    # 3. Approve (Manager)
    s = requests.Session()
    if not login(s, **MANAGER_CREDS): return False
    
    r = s.get(f"{BASE_URL}/approval/inbox")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.find_all('a', href=True)
    target_link = None
    for l in links:
        if "/approval/" in l['href'] and "EXPENSE" in l.text:
            target_link = l['href']
            break # Approve the first one found
            
    if target_link:
        req_id = target_link.split('/')[-1]
        print(f"[OK] Found Pending Expense Request ID: {req_id}")
        r = s.post(f"{BASE_URL}/approval/{req_id}/action", data={'action': 'APPROVE', 'comment': 'Okay'})
        if "성공적으로 처리되었습니다" in r.text:
             print("[OK] Expense Request Approved")
        else:
             print("[FAIL] Expense Approval Failed")
             return False
    else:
        print("[FAIL] No Pending Expense Request found")
        return False
        
    return True

def test_cert_flow():
    print("\n--- Testing Certificate Flow ---")
    s = requests.Session()
    if not login(s, **EMPLOYEE_CREDS): return False
    
    data = {
        'cert_type': 'EMPLOYMENT',
        'issue_to': 'Bank',
        'reason': 'Loan'
    }
    r = s.post(f"{BASE_URL}/certificate/request", data=data)
    if "증명서 발급 신청이 되었습니다" in r.text:
        print("[OK] Certificate Requested")
    else:
        print("[FAIL] Cert Request Failed")
        return False
    s.close()
    
    # Admin Approval
    s = requests.Session()
    if not login(s, **ADMIN_CREDS): return False
    
    r = s.get(f"{BASE_URL}/approval/inbox")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.find_all('a', href=True)
    target_link = None
    for l in links:
        if "/approval/" in l['href'] and "CERTIFICATE" in l.text:
            target_link = l['href']
            break
            
    if target_link:
        req_id = target_link.split('/')[-1]
        r = s.post(f"{BASE_URL}/approval/{req_id}/action", data={'action': 'APPROVE', 'comment': 'Issued'})
        if "성공적으로 처리되었습니다" in r.text:
             print("[OK] Certificate Approved")
        else:
             print("[FAIL] Cert Approval Failed")
             return False
    else:
        print("[FAIL] No Pending Cert Request found")
        return False
        
    return True

if __name__ == "__main__":
    if test_leave_flow() and test_expense_flow() and test_cert_flow():
        print("\n[SUCCESS] All System Tests Passed!")
    else:
        print("\n[FAIL] Some tests failed.")
