import os
import requests
import base64
from app import create_app
from app.services.stamp_service import StampService

def check_font_system():
    print("=== 1. Checking File System ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path_a = os.path.join(base_dir, 'app', 'static', 'fonts', 'HJJeonseoA.ttf')
    
    if os.path.exists(font_path_a):
        size = os.path.getsize(font_path_a)
        print(f"[PASS] File found: {font_path_a}")
        print(f"       Size: {size} bytes")
    else:
        print(f"[FAIL] File NOT found at: {font_path_a}")

    print("\n=== 2. Checking Server Response ===")
    try:
        url = "http://127.0.0.1:5000/static/fonts/HJJeonseoA.ttf"
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            print(f"[PASS] Server returned 200 OK")
            print(f"       Content-Length: {r.headers.get('content-length')}")
            print(f"       Content-Type: {r.headers.get('content-type')}")
        else:
            print(f"[FAIL] Server returned status code: {r.status_code}")
    except Exception as e:
        print(f"[FAIL] Could not connect to server: {e}")

    print("\n=== 3. Checking SVG Generation Logic ===")
    app = create_app()
    with app.app_context():
        try:
            # Create a mock spec for Jeonseo
            target_text = "(주)휴넷가이아"
            print(f"Generating stamp for: {target_text}")
            
            spec = {
                "type": "corp_circular", 
                "font_style": "jeonseo",
                "text": target_text,
                "width": 150, "height": 150, "color": "red"
            }
            # Note: The service might expand (주) -> 주식회사 automatically
            svg = StampService.generate_svg(target_text, spec, "corporate")
            
            # CRITICAL: For local file viewing, we must EMBED the font.
            # Relative URL /static/fonts/... fails on file:// protocol.
            if os.path.exists(font_path_a):
                with open(font_path_a, "rb") as font_file:
                    b64_font = base64.b64encode(font_file.read()).decode('utf-8')
                
                # Replace the src url with data uri
                # StampService uses: src: url('/static/fonts/HJJeonseoA.ttf') format('truetype');
                old_src = "url('/static/fonts/HJJeonseoA.ttf')"
                new_src = f"url('data:font/ttf;base64,{b64_font}')"
                svg = svg.replace(old_src, new_src)
                print("[INFO] Embedded font as Base64 for local viewing")
            
            output_file = "test_corp_stamp.svg"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(svg)
            print(f"[PASS] Saved generated SVG to {output_file}")

            # Verification
            if "HJJeonseoA" in svg or "HJJeonseoB" in svg:
                print("[PASS] SVG uses 'HJJeonseo' font family")
            else:
                print("[FAIL] SVG does NOT use 'HJJeonseo' font")
                
            if "(주)휴넷가이아" in svg and "주식회사 휴넷가이아" not in svg:
                 print("[PASS] Text preserved exactly ((주) maintained)")
            else:
                 print("[FAIL] Text logic failed: Content might have been altered")
            
            print(f"--- CSS Snippet ---\n{svg[:600]}...")
            
        except Exception as e:
            print(f"[FAIL] SVG Generation Error: {e}")

if __name__ == "__main__":
    check_font_system()
