import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def print_result(test_name, success, details=""):
    status = "PASS" if success else "FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"       -> {details}")

def run_security_tests():
    print("--- เริ่มการทดสอบความปลอดภัย API ---")
    
    # Test 1: No Token Access
    res = requests.get(f"{BASE_URL}/auth/me")
    print_result("Test 1: เข้าถึง API โดยไม่มี Token", 
                 res.status_code == 401, 
                 f"Status: {res.status_code} (คาดหวัง: 401)")

    # Test 2: Invalid Token Format
    headers = {"Authorization": "Bearer INVALID_TOKEN_FORMAT"}
    res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_result("Test 2: เข้าถึง API ด้วย Token ปลอม", 
                 res.status_code == 401,
                 f"Status: {res.status_code} (คาดหวัง: 401)")

    # Test 3: SQL Injection Attempt on Login (Very basic check, ORM should block this)
    payload = {"username": "admin' OR '1'='1", "password": "password"}
    res = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print_result("Test 3: SQL Injection (Login)", 
                 res.status_code in [400, 401], 
                 f"Status: {res.status_code} (คาดหวัง: 401 หรือ 400)")

    # Test 4: Missing Fields in Login
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin"})
    print_result("Test 4: ส่งข้อมูล Login ไม่ครบถ้วน", 
                 res.status_code == 400, 
                 f"Status: {res.status_code} (คาดหวัง: 400)")
    
    print("--- จบการทดสอบ ---")

if __name__ == "__main__":
    try:
        run_security_tests()
    except requests.exceptions.ConnectionError:
        print("FAIL | Cannot connect to server. Please run Flask app first.")
