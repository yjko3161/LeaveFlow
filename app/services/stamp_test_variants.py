from stamp_service import StampService
import os

if __name__ == "__main__":
    base_spec = {
        "shape": "circle",
        "width": 160,
        "height": 160,
        "layout": "corp_circular",
        "font_size": 44,
        "symbol": "●",
        "embed_fonts": True, # Ensure standalone viewing
        "outer_text_radius": 62,
        "outer_font_size": 18,
        "outer_text_dy": 24,
        "inner_ring_radius": 48,
        "inner_text_y_shift": 8,
        "inner_font_size": 28,
        "inner_line_gap": 30,
        "reverse_outer_path": False
    }

    test_cases = [
        ("stamp_jeonseo_hangul.svg", "대표이사"),
        ("stamp_jeonseo_hanja.svg", "代表理事") # Verify Hanja support
    ]
    
    os.makedirs("out_variants", exist_ok=True)

    for filename, inner_txt in test_cases:
        spec = base_spec.copy()
        spec["inner_text"] = inner_txt
        
        # Test text: 아이가넷휴(주)
        svg = StampService.generate_svg("아이가넷휴(주)", spec, group="corp")
        
        out_path = os.path.join("out_variants", filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Generated: {out_path} (Size: {len(svg)} bytes)")
