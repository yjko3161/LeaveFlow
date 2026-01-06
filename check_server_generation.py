import sys
import os

# Ensure app is in path
sys.path.append(os.getcwd())

from app import create_app

def check_server_gen():
    app = create_app()
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = True # Bypass login for this test

    with app.test_client() as client:
        url = "/stamp/preview?text=(주)휴넷가이아&font_style=jeonseo&type=corp"
        print(f"Requesting stamp from {url}...")
        
        # Flask test client returns a Response object
        r = client.get(url)
        
        if r.status_code == 200:
            content_len = len(r.data)
            print(f"[INFO] Response Status: 200 OK")
            print(f"[INFO] Response Length: {content_len} bytes")
            
            payload = r.data.decode('utf-8')
            
            if content_len > 50000:
                print("[PASS] Response is large, suggesting Base64 embedding succeeded.")
                # Look for data uri
                if "data:font/ttf;base64," in payload[:100000]: 
                   print("[PASS] Found 'data:font/ttf;base64,' in SVG.")
                else:
                   print("[WARN] Base64 header not found in first 100KB.")
            else:
                print("[FAIL] Response is too small (<50KB). Embedding likely failed.")
                print(f"Snippet: {payload[:500]}")
        else:
            print(f"[FAIL] Server returned {r.status_code}")
            print(r.data.decode('utf-8')[:500])

if __name__ == "__main__":
    check_server_gen()
