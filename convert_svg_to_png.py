import os
import cairosvg

def convert():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    svg_path = os.path.join(base_dir, 'test_corp_stamp.svg')
    png_path = os.path.join(base_dir, 'test_corp_stamp.png')
    
    # CairoSVG relies on system fonts or fontconfig. 
    # For now, let's just convert and see if it picks it up or falls back.
    # The SVG has @font-face with a localized URL /static/fonts... 
    # CairoSVG won't resolve that relative URL well without a base_url or filesystem path.
    # We should inject the @font-face with raw base64 or absolute path?
    # Let's try simple conversion first.
    
    print(f"Converting {svg_path} to {png_path} using CairoSVG...")
    try:
        cairosvg.svg2png(url=svg_path, write_to=png_path)
        print("Done.")
    except Exception as e:
        print(f"CairoSVG failed: {e}")

if __name__ == "__main__":
    convert()
