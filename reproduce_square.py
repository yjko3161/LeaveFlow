from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
import io
import re
import os

# 1. Register Fonts (Simulating stamp.py)
font_configs = [
    {"name": "MalgunGothic", "path": "C:/Windows/Fonts/malgun.ttf"},
    {"name": "MalgunGothic-Bold", "path": "C:/Windows/Fonts/malgunbd.ttf"}
]
primary_font = "Helvetica"
has_bold = False

for config in font_configs:
    if os.path.exists(config["path"]):
        try:
            pdfmetrics.registerFont(TTFont(config["name"], config["path"]))
            if config["name"] == "MalgunGothic":
                primary_font = config["name"]
            if config["name"] == "MalgunGothic-Bold":
                has_bold = True
        except:
            pass

if primary_font == "MalgunGothic" and has_bold:
    addMapping('MalgunGothic', 0, 0, 'MalgunGothic') # normal
    addMapping('MalgunGothic', 1, 0, 'MalgunGothic-Bold') # bold

# 2. Use a Square Stamp SVG (simulated content from StampService)
width, height = 90, 90
color = "red"
font_family = "MalgunGothic" # This is what we expect to map to
font_size = 36
text = "이" 
# Case: Single character in square grid, often bold
svg_content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
svg_content += f'<rect x="2" y="2" width="{width-4}" height="{height-4}" fill="none" stroke="{color}" stroke-width="3" />'
svg_content += f'<text x="{width/2}" y="{height/2}" font-family="{font_family}" font-size="{font_size*1.5}" fill="{color}" text-anchor="middle" dominant-baseline="middle" font-weight="bold">{text}</text>'
svg_content += '</svg>'

# 3. Preprocess (Simulating stamp.py)
# Remove <style>
svg_text = re.sub(r'<style>.*?</style>', '', svg_content, flags=re.DOTALL)
# Map font-family
svg_text = re.sub(r'font-family=["\'](.*?)["\']', f'font-family="{primary_font}"', svg_text)
# Strip dominant-baseline
svg_text = svg_text.replace('dominant-baseline="middle"', '')

# 4. Render
print(f"Rendering SVG: {svg_text}")
drawing = svg2rlg(io.BytesIO(svg_text.encode('utf-8')))
renderPM.drawToFile(drawing, "reproduce_square.png", fmt="PNG")

if os.path.exists("reproduce_square.png"):
    print(f"PNG created: {os.path.getsize('reproduce_square.png')} bytes")
else:
    print("PNG creation failed")
