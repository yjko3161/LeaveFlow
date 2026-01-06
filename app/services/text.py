from PIL import Image, ImageDraw, ImageFont
import os

def make_stamp_png(
    text: str,
    font_path: str,
    out_path: str = "stamp.png",
    size: int = 512,              # 최종 이미지 한 변(px)
    padding: int = 40,            # 테두리-글씨 여백
    border: int = 12,             # 테두리 두께
    shape: str = "circle",        # "circle" or "square"
    color=(255, 0, 0, 255),       # RGBA (빨강)
    add_in_suffix=True,           # 2~3글자면 "인" 자동 붙이기
):
    # 1) 텍스트 전처리
    txt = text.strip()
    if add_in_suffix and (len(txt) < 4) and (not txt.endswith("인")):
        txt += "인"

    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font not found: {font_path}")

    # 2) 캔버스(투명)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 3) 테두리 그리기
    box = (border//2, border//2, size - border//2 - 1, size - border//2 - 1)
    if shape == "circle":
        draw.ellipse(box, outline=color, width=border)
    elif shape == "square":
        draw.rectangle(box, outline=color, width=border)
    else:
        raise ValueError("shape must be 'circle' or 'square'")

    # 4) 글씨 크기 자동 맞추기
    #    (대충 큰 폰트부터 줄여가며 중앙 영역에 들어가게)
    target_w = size - 2 * (padding + border)
    target_h = size - 2 * (padding + border)

    font_size = size  # 시작 크게
    font = ImageFont.truetype(font_path, font_size)

    # 여러 줄(세로 도장 느낌) 옵션: 여기선 기본은 한 줄
    # 필요하면 세로배치로 바꿔줄 수도 있음.
    while True:
        bbox = draw.textbbox((0, 0), txt, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= target_w and h <= target_h:
            break
        font_size -= 4
        if font_size <= 10:
            break
        font = ImageFont.truetype(font_path, font_size)

    # 5) 중앙 정렬로 텍스트 그리기
    x = (size - w) // 2
    y = (size - h) // 2
    draw.text((x, y), txt, font=font, fill=color)

    # 6) 저장
    img.save(out_path, "PNG")
    return out_path

if __name__ == "__main__":
    # 폰트 파일 경로 수정 (프로젝트 내 경로 사용)
    font_path = r"c:\USERS\USER\APPDATA\LOCAL\MICROSOFT\WINDOWS\FONTS\HJ한전서A.TTF"
    make_stamp_png("고유진", font_path, out_path="stamp_go.png", shape="circle")
    make_stamp_png("휴넷가이아", font_path, out_path="stamp_hu.png", shape="square")
    print("done")