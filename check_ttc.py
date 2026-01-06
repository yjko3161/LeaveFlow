from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

ttc_files = ["C:/Windows/Fonts/batang.ttc", "C:/Windows/Fonts/gulim.ttc", "C:/Windows/Fonts/malgun.ttc"]

for ttc in ttc_files:
    if os.path.exists(ttc):
        print(f"\nChecking {ttc}...")
        # Try to register first few indices
        for i in range(4):
            try:
                name = f"Font_{os.path.basename(ttc)}_{i}"
                pdfmetrics.registerFont(TTFont(name, ttc, index=i))
                print(f"  Successfully registered index {i} as {name}")
            except Exception as e:
                print(f"  Failed index {i}: {e}")
    else:
        print(f"\n{ttc} NOT FOUND.")
