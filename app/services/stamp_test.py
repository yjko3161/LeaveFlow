from stamp_service import StampService

if __name__ == "__main__":
    spec = {
        "shape": "circle",
        "width": 160,
        "height": 160,
        "layout": "corp_circular",
        "font_size": 44,
        "symbol": "●",

        "seal_font_files": ["HJJeonseoA.ttf"],   # 네 폰트명으로 바꿔
        "seal_font_family": "JeonseoSeal",
        "embed_fonts": True,

        "outer_text_radius": 58,   # Reduced radius to pull text inward (62 -> 58)
        "outer_font_size": 18,
        "outer_text_dy": 28,   # Increased dy (26->28) and reduced font (20->18) for centering
        "inner_ring_radius": 48,
        "inner_text": "대표이사",
        "inner_text_y_shift": 8,
        "inner_font_size": 28,
        "inner_line_gap": 30,
        "reverse_outer_path": False
    }

    svg = StampService.generate_svg("(주)휴넷가이아", spec, group="corp")
    with open("stamp_out.svg", "w", encoding="utf-8") as f:
        f.write(svg)

    print("OK -> stamp_out.svg 생성됨")
