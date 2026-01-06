import os
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont

def check_font(font_path, chars):
    print(f"Checking font: {font_path}")
    try:
        font = TTFont('TestFont', font_path)
        
        # Determine available glyphs
        # reportlab TTFont exposes 'face' but getting cmap might be tricky depending on version.
        # But we can try to get glyph names or width for chars.
        # If a char is missing, getWidth usually returns 0 or default width?
        # Actually TTFont.makeCharSet might be useful, or checking font.face.charToGlyph
        
        missing = []
        present = []
        
        # Accessing the cmap directly if possible
        # font.face.charToGlyph is a dictionary mapping char code to glyph index
        cmap = font.face.charToGlyph
        
        for char in chars:
            code = ord(char)
            if code in cmap:
                present.append(char)
                # print(f"  [OK] {char} (U+{code:04X}) -> Glyph {cmap[code]}")
            else:
                missing.append(char)
                print(f"  [MISSING] {char} (U+{code:04X})")
                
        if not missing:
            print("  => ALL CHARACTERS SUPPORTED")
        else:
            print(f"  => MISSING {len(missing)} CHARACTERS")

    except Exception as e:
        print(f"  [ERROR] Could not parse font: {e}")

base_dir = os.path.dirname(os.path.abspath(__file__))
font_dir = os.path.join(base_dir, "app/static/fonts")

chars_to_check = "휴넷가이아주대표이사" # User's company name chars + common ones

font_a = os.path.join(font_dir, "HJJeonseoA.ttf")
font_b = os.path.join(font_dir, "HJJeonseoB.ttf")

check_font(font_a, chars_to_check)
check_font(font_b, chars_to_check)
