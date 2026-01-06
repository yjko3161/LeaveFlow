import math
import io
import re
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 1. Setup Environment
font_path = "C:/Windows/Fonts/batang.ttc"
pdfmetrics.registerFont(TTFont('Batang', font_path))

# 2. Simulate StampService manual rotation logic
width, height = 120, 120
color = "red"
font_family = "Batang"
font_size = 36
text = "휴넷가이아"
outer_text_val = f"주식회사 {text}"
inner_text_val = "대표이사"
symbol = "●"
r_outer = 50

svg_content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
# Symbol at Top
svg_content += f'<text x="{width/2}" y="{height/2 - r_outer}" font-family="{font_family}" font-size="{font_size * 0.4}" fill="{color}" text-anchor="middle">{symbol}</text>'

# Manual Rotation for Outer Text
char_count = len(outer_text_val)
arc_angle = min(200, 18 * char_count)
start_angle = 180 - (arc_angle / 2)
step_angle = arc_angle / (char_count - 1 if char_count > 1 else 1)

for i, char in enumerate(outer_text_val):
    angle = start_angle + (i * step_angle)
    rad = math.radians(angle - 90)
    tx = width/2 + r_outer * math.cos(rad)
    ty = height/2 + r_outer * math.sin(rad)
    svg_content += f'<text x="{tx}" y="{ty}" font-family="{font_family}" font-size="{font_size * 0.45}" fill="{color}" text-anchor="middle" font-weight="bold" transform="rotate({angle}, {tx}, {ty})">{char}</text>'

# Inner Circle & Text
r_inner = width * 0.21
svg_content += f'<circle cx="{width/2}" cy="{height/2}" r="{r_inner}" stroke="{color}" stroke-width="1.5" fill="none" />'
chars = ["대", "표", "이", "사"]
p_dist = r_inner * 0.45
v_off = p_dist * 0.8
positions = [(width/2 + p_dist, height/2 - v_off), (width/2 + p_dist, height/2 + v_off), (width/2 - p_dist, height/2 - v_off), (width/2 - p_dist, height/2 + v_off)]
for char, pos in zip(chars, positions):
    svg_content += f'<text x="{pos[0]}" y="{pos[1]}" font-family="{font_family}" font-size="{font_size*0.48}" fill="{color}" text-anchor="middle" font-weight="bold">{char}</text>'
svg_content += '</svg>'

# 3. Simulate Download Preprocessing
svg_processed = re.sub(r'dominant-baseline="middle"', '', svg_content)

# 4. Convert and Save
drawing = svg2rlg(io.BytesIO(svg_processed.encode('utf-8')))
renderPM.drawToFile(drawing, "final_verify.png", fmt="PNG")
print(f"File created: {os.path.exists('final_verify.png')}, Size: {os.path.getsize('final_verify.png')}")
