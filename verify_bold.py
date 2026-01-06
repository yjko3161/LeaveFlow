from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics import renderPM
import os

# 1. Register Fonts
korean_font_path = "C:/Windows/Fonts/malgun.ttf"
korean_bold_path = "C:/Windows/Fonts/malgunbd.ttf"
font_name = "MalgunGothic"
bold_font_name = "MalgunGothic-Bold"

if os.path.exists(korean_font_path) and os.path.exists(korean_bold_path):
    print("Found both font files.")
    try:
        pdfmetrics.registerFont(TTFont(font_name, korean_font_path))
        pdfmetrics.registerFont(TTFont(bold_font_name, korean_bold_path))
        
        # 2. Add Mapping
        addMapping(font_name, 0, 0, font_name)
        addMapping(font_name, 1, 0, bold_font_name)
        print("Fonts registered and mapped.")
        
        # 3. Test Rendering
        d = Drawing(400, 200)
        # Normal Text
        d.add(String(10, 150, "Normal Text (Malgun) - 한글 테스트", fontName=font_name, fontSize=20, fillColor='black'))
        
        # Bold Text - ReportLab should automatically pick the bold font if we ask for the base font name + bold flag?
        # Actually, in ReportLab graphics (Drawing/String), we usually specify fontName directly.
        # But svglib uses the mapping when it encounters font-weight="bold".
        # To test the MAPPING, we ideally simulate svglib's behavior or use ReportLab's paragraph engine, but for low-level graphics:
        
        # Let's test if we can explicitly use the Bold font name, which svglib would resolve to.
        d.add(String(10, 100, "Bold Text (MalgunBold) - 한글 테스트", fontName=bold_font_name, fontSize=20, fillColor='red'))
        
        renderPM.drawToFile(d, "test_bold_map.png", fmt="PNG")
        if os.path.exists("test_bold_map.png"):
            print(f"PNG Success: {os.path.getsize('test_bold_map.png')} bytes")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Font files not found.")
