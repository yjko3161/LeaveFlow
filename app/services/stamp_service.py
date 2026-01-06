import html
import os
import base64


class StampService:
    @staticmethod
    def generate_svg(text, template_spec, group="general"):
        text = html.escape(text)

        # suffix
        if template_spec.get("add_in_suffix") and not text.endswith("인") and len(text) < 4:
            text += "인"

        width = int(template_spec.get("width", 120))
        height = int(template_spec.get("height", 120))
        color = template_spec.get("color", "#ff0000")
        shape = template_spec.get("shape", "circle")
        layout = template_spec.get("layout", "center")

        # =========================================================
        # 1) 진서체(HJJeonseoA/B) 강제 로딩 (정적 파일로)
        #    - 너 폴더: app/static/fonts
        #    - URL: /static/fonts/xxx.ttf (Flask static 기본)
        # =========================================================
        base_dir = os.path.dirname(os.path.abspath(__file__))
        static_font_dir = os.path.abspath(os.path.join(base_dir, "..", "static", "fonts"))
        
        # Embed both fonts to ensure full character coverage (Hangul + Hanja)
        # Embed both fonts to ensure full character coverage (Hangul + Hanja)
        # B is likely bolder/better for Hanja, A for Hangul.
        # We allow fallback: prefer B, then A.
        # UPDATE: HJJeonseoA lacks modern Hangul glyphs. We use H2MKPB (Mokpan) as a fallback for outer text.
        seal_fonts = [
            (r"c:\USERS\USER\APPDATA\LOCAL\MICROSOFT\WINDOWS\FONTS\HJ한전서A.TTF", "JeonseoSealA_User"),
            ("HJJeonseoB.ttf", "JeonseoSealB"),
            ("HJJeonseoA.ttf", "JeonseoSealA"),
            ("H2MKPB.TTF", "MokpanSeal")
        ]
        
        embed_fonts = bool(template_spec.get("embed_fonts", False))
        font_css = ""
        
        for f_file, f_family in seal_fonts:
            # Handle absolute paths (user provided) vs relative paths (static/fonts)
            if os.path.isabs(f_file):
                f_path = f_file
            else:
                f_path = os.path.join(static_font_dir, f_file)

            if os.path.exists(f_path):
                if embed_fonts:
                    # print(f"[DEBUG] Embedding font {f_file} as {f_family}...")
                    with open(f_path, "rb") as fp:
                        b64 = base64.b64encode(fp.read()).decode("utf-8")
                    font_css += f"""
                    @font-face {{
                      font-family: '{f_family}';
                      src: url('data:font/ttf;base64,{b64}') format('truetype');
                      font-weight: 400;
                      font-style: normal;
                    }}
                    """
                else:
                    # For absolute paths outside static dir, direct URL linking won't work easily
                    # unless served via a specific route. For now, assume embedding or ignore URL if absolute.
                    # But for stamp_test (local), embedding is what matters.
                    font_css += f"""
                    @font-face {{
                      font-family: '{f_family}';
                      src: url('/static/fonts/{os.path.basename(f_file)}') format('truetype');
                      font-weight: 400;
                      font-style: normal;
                    }}
                    """
            else:
                pass 
                # print(f"[ERROR] Font file not found: {f_path}")

        # Use font stack: Try User's Font first
        outer_font = "JeonseoSealA_User"
        # Inner text (Hanja) is better with JeonseoSealB (bolder)
        inner_font = "JeonseoSealB"

        font_size = float(template_spec.get("font_size", 36))

        # ring thickness
        ring_thickness_outer = float(template_spec.get("ring_thickness_outer", 6.0))
        ring_thickness_inner = float(template_spec.get("ring_thickness_inner", 3.0))

        # ---------------------------
        # 도넛 링(채움) 생성
        # ---------------------------
        def ring_circle(cx, cy, r_outer, thickness, fill_color):
            r_inner = max(0.0, r_outer - thickness)
            outer = (
                f"M {cx} {cy - r_outer} "
                f"A {r_outer} {r_outer} 0 1 1 {cx} {cy + r_outer} "
                f"A {r_outer} {r_outer} 0 1 1 {cx} {cy - r_outer} Z "
            )
            inner = (
                f"M {cx} {cy - r_inner} "
                f"A {r_inner} {r_inner} 0 1 0 {cx} {cy + r_inner} "
                f"A {r_inner} {r_inner} 0 1 0 {cx} {cy - r_inner} Z "
            )
            return f'<path fill="{fill_color}" stroke="none" fill-rule="evenodd" d="{outer}{inner}"/>'

        svg_parts = []
        svg_parts.append(
            f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
xmlns="http://www.w3.org/2000/svg">
<style>
{font_css}
</style>
'''
        )

        cx, cy = width / 2, height / 2
        minwh = min(width, height)

        # =========================================================
        # 2) 법인 인감(상용 구조 동일) : corp_circular
        #    - 외곽 링
        #    - 외곽 원호 글자 textPath
        #    - 상단 심볼
        #    - 내부 링(크게)
        #    - 내부 2줄(대표/이사)
        # =========================================================
        if layout == "corp_circular":
            # 1) 외곽 링
            r_outer = (minwh / 2) - 1
            svg_parts.append(ring_circle(cx, cy, r_outer, ring_thickness_outer, color))

            # 2) 외곽 textPath 경로
            r_text = float(template_spec.get("outer_text_radius", (minwh / 2) - 22)) 
            path_id = "outerPath"

            # 기본 path: 6시(하단)에서 시작하여 시계방향으로 회전 (6 -> 9 -> 12 -> 3 -> 6)
            # 이렇게 해야 7시~11시 구간(좌측)을 끊김 없이 표현 가능
            svg_parts.append(f'''
<defs>
  <path id="{path_id}" d="
    M {cx} {cy + r_text}
    A {r_text} {r_text} 0 1 1 {cx} {cy - r_text}
    A {r_text} {r_text} 0 1 1 {cx} {cy + r_text}
  " />
</defs>
''')

            # 3) 회사명 정규화 & 우횡서(Right-to-Left) 처리
            outer_text = text.strip()
            
            # (주) 포맷 통일
            outer_text = outer_text.replace("(주)", "（주）")
            outer_text = outer_text.replace("(", "（").replace(")", "）")

            # ★ 사용자 요청: 텍스트 좌측 (~7시 시작) 배치
            
            outer_font_size = float(template_spec.get("outer_font_size", font_size * 0.4))

            # ★ 핵심: 하단 아치로 내리는 값 (샘플 느낌)
            outer_dy = float(template_spec.get("outer_text_dy", 0))

            # ★ 핵심: 텍스트 시작 위치 (6시 기준 0%)
            # 7시는 약 8% 지점. 넉넉히 10% 부터 시작해봄
            outer_start_offset = template_spec.get("outer_start_offset", "10%")

            # 글자 방향 뒤집힘 옵션
            reverse_path = bool(template_spec.get("reverse_outer_path", False))
            if reverse_path:
                path_id2 = "outerPathRev"
                svg_parts.append(f'''
<defs>
  <path id="{path_id2}" d="
    M {cx + r_text} {cy}
    A {r_text} {r_text} 0 1 1 {cx - r_text} {cy}
    A {r_text} {r_text} 0 1 1 {cx + r_text} {cy}
  " />
</defs>
''')
                path_use = path_id2
            else:
                path_use = path_id

            # Adjust character spacing for better arc distribution
            letter_spacing = float(template_spec.get("outer_letter_spacing", "2.0"))

      # ★ Text Anchor: Start (시작점 기준 정렬), Offset: 27% (12시 도트 약간 우측)
            svg_parts.append(f'''
<text fill="{color}"
      font-family="{outer_font}"
      font-size="{outer_font_size}"
      font-weight="400"
      letter-spacing="{letter_spacing}">
  <textPath href="#{path_use}" startOffset="{outer_start_offset}" text-anchor="start" dy="{outer_dy}">
    {outer_text}
  </textPath>
</text>
''')

            # 4) 상단 심볼
            symbol = template_spec.get("symbol", "●")
            symbol_size = float(template_spec.get("symbol_size", font_size * 0.50))
            symbol_y = cy - r_text + float(template_spec.get("symbol_y_offset", 1.0))
            svg_parts.append(
                f'''<text x="{cx}" y="{symbol_y}"
font-family="{outer_font}" font-size="{symbol_size}"
fill="{color}" text-anchor="middle" dominant-baseline="middle"
font-weight="400">{symbol}</text>'''
            )

            # 5) 내부 링 (더 크게)
            r_inner = float(template_spec.get("inner_ring_radius", (minwh / 2) * 0.58))
            svg_parts.append(ring_circle(cx, cy, r_inner, ring_thickness_inner, color))

            # 6) 내부 글자(2줄 vs 2x2 Grid)
            inner_text_val = template_spec.get("inner_text", "대표이사").strip()

            # ★ [복구] 전서체/법인인감일 경우 한자 자동 변환
            # 사용자가 한글 "대표이사"를 넣어도 실제 출력은 "代表理事"가 나오도록 함
            if inner_text_val == "대표이사":
                 inner_text_val = "代表理事"

            inner_font_size = float(template_spec.get("inner_font_size", font_size * 0.56))
            inner_shift = float(template_spec.get("inner_text_y_shift", 0.0))

            # 4글자는 무조건 2x2 Vertical Column 배치 (전서체 정석)
            # 입력: "대표이사" ->
            #   오른쪽 열: 대(T), 표(B)
            #   왼쪽 열: 이(T), 사(B)
            if len(inner_text_val) == 4:
                # 좌표 계산 helpers
                # 중심(cx, cy) 기준 offset
                dx = inner_font_size * 0.55  # 좌우 간격
                dy = inner_font_size * 0.55  # 상하 간격
                
                # 순서: 대(0), 표(1), 이(2), 사(3)
                # TR: (cx+dx, cy-dy) -> 대
                # BR: (cx+dx, cy+dy) -> 표
                # TL: (cx-dx, cy-dy) -> 이
                # BL: (cx-dx, cy+dy) -> 사
                coords = [
                    (cx + dx, cy - dy + inner_shift), # 0: 대 (TR)
                    (cx + dx, cy + dy + inner_shift), # 1: 표 (BR)
                    (cx - dx, cy - dy + inner_shift), # 2: 이 (TL)
                    (cx - dx, cy + dy + inner_shift), # 3: 사 (BL)
                ]
                
                for i, char in enumerate(inner_text_val):
                     tx, ty = coords[i]
                     svg_parts.append(f'''
<text x="{tx}" y="{ty}"
      font-family="{inner_font}"
      font-size="{inner_font_size}"
      fill="{color}"
      text-anchor="middle"
      dominant-baseline="middle"
      font-weight="400">{char}</text>
''')

            else:
                # 기존 2줄 로직 (3글자 이하 또는 5글자 이상)
                if inner_text_val in ("대표이사", "代表理事"): # Hard fallback just in case
                     line1, line2 = inner_text_val[:2], inner_text_val[2:]
                else:
                    mid = max(1, len(inner_text_val) // 2)
                    line1, line2 = inner_text_val[:mid], inner_text_val[mid:]

                gap = float(template_spec.get("inner_line_gap", inner_font_size * 0.95))
                y1 = cy + inner_shift - gap / 2
                y2 = cy + inner_shift + gap / 2

                svg_parts.append(f'''
<text x="{cx}" y="{y1}"
      font-family="{inner_font}"
      font-size="{inner_font_size}"
      fill="{color}"
      text-anchor="middle"
      dominant-baseline="middle"
      font-weight="400">{line1}</text>
<text x="{cx}" y="{y2}"
      font-family="{inner_font}"
      font-size="{inner_font_size}"
      fill="{color}"
      text-anchor="middle"
      dominant-baseline="middle"
      font-weight="400">{line2}</text>
''')

        else:
            # general 최소 동작
            r_outer = (minwh / 2) - 1
            if shape == "circle":
                svg_parts.append(ring_circle(cx, cy, r_outer, ring_thickness_outer, color))

            svg_parts.append(
                f'''<text x="{cx}" y="{cy}"
font-family="{outer_font}" font-size="{font_size}"
fill="{color}" text-anchor="middle" dominant-baseline="middle"
font-weight="400">{text}</text>'''
            )

        svg_parts.append("</svg>")
        return "".join(svg_parts)

    @staticmethod
    def get_default_templates():
        return [
            # 법인 인감(진서체 고정)
            {"code": "CP_01", "group": "corp", "spec": {
                "shape": "circle",
                "width": 120, "height": 120,
                "layout": "corp_circular",
                "font_size": 36,

                "symbol": "●",
                "embed_fonts": True,          # Changed to True to enforce Base64 embedding for custom fonts

                # 샘플 느낌 기본값
                "ring_thickness_outer": 6.0,
                "ring_thickness_inner": 3.0,

                "outer_text_radius": 46,
                "outer_font_size": 14,
                "outer_text_dy": 18,           # ★ 외곽문자 하단 배치 핵심

                "inner_ring_radius": 35,       # 필요하면 더 키워도 됨 (ex 38~40)
                "inner_text_y_shift": 6.0,     # ★ 내부 글자만 아래로

                "inner_font_size": 20,
                "inner_line_gap": 20,

                "reverse_outer_path": True    # 글자 방향 이상하면 True
            }},
        ]
