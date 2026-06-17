"""
인스타그램 공유 카드 생성기
- 피드용: 1080x1080 (1:1)
- 스토리/릴스용: 1080x1920 (9:16)
- 무료: 워터마크 포함
- 프리미엄: 워터마크 없음
"""
from PIL import Image, ImageDraw, ImageFont
import os
import math
from datetime import date

# 브랜드 컬러 (앱과 동일)
COLOR_BG        = (30, 30, 30)          # #1E1E1E
COLOR_CARD      = (42, 42, 42)          # #2A2A2A
COLOR_RED       = (139, 26, 26)         # #8B1A1A
COLOR_GOLD      = (201, 168, 76)        # #C9A84C
COLOR_IVORY     = (250, 243, 224)       # #FAF3E0
COLOR_GREEN     = (76, 175, 80)         # #4CAF50
COLOR_WHITE     = (245, 245, 245)
COLOR_GRAY      = (170, 170, 170)
COLOR_WATERMARK = (255, 255, 255, 60)   # 반투명 흰색


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Windows 한글 폰트 로드 (없으면 기본 폰트)"""
    candidates = [
        "C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/NanumGothic.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.ellipse([x0, y0, x0 + radius * 2, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y0, x1, y0 + radius * 2], fill=fill)
    draw.ellipse([x0, y1 - radius * 2, x0 + radius * 2, y1], fill=fill)
    draw.ellipse([x1 - radius * 2, y1 - radius * 2, x1, y1], fill=fill)


def _draw_progress_ring(draw, cx, cy, r, pct, color_bg, color_fg, thickness=18):
    """원형 프로그레스 링"""
    bbox = [cx - r, cy - r, cx + r, cy + r]
    draw.arc(bbox, 0, 360, fill=color_bg, width=thickness)
    angle = min(pct / 100 * 360, 360)
    if angle > 0:
        draw.arc(bbox, -90, -90 + angle, fill=color_fg, width=thickness)


def _add_watermark(img: Image.Image) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    font = _font(28)
    text = "소고기식단 트래커 | 무료버전"
    # 대각선 반복 워터마크
    for y in range(0, img.height, 220):
        for x in range(-200, img.width, 400):
            d.text((x, y), text, font=font, fill=COLOR_WATERMARK)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def create_feed_card(
    protein: float, protein_goal: float,
    calories: float, calorie_goal: float,
    fat: float,
    beef_g: float,
    weight_kg: float | None,
    day_str: str,
    is_premium: bool = False,
    challenge_day: int | None = None,
) -> Image.Image:
    """
    인스타그램 피드용 1080x1080 카드
    """
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # ── 배경 그라데이션 효과 (상단 레드 포인트) ──────────────────
    for i in range(300):
        alpha = int(80 * (1 - i / 300))
        draw.ellipse(
            [W // 2 - 300 + i // 2, -200 + i // 2, W // 2 + 300 - i // 2, 200 - i // 2],
            fill=(139, 26, 26, alpha) if False else COLOR_RED,
        )

    # 상단 레드 배너
    draw.rectangle([0, 0, W, 120], fill=COLOR_RED)

    # 타이틀
    draw.text((W // 2, 38), "🥩 소고기 식단 트래커", font=_font(44, True),
              fill=COLOR_IVORY, anchor="mm")
    draw.text((W // 2, 90), day_str, font=_font(26),
              fill=COLOR_IVORY, anchor="mm")

    # 챌린지 뱃지
    if challenge_day:
        badge_text = f"D+{challenge_day} 50일 챌린지"
        _draw_rounded_rect(draw, [W - 230, 130, W - 30, 175], 8, COLOR_GOLD)
        draw.text((W - 130, 152), badge_text, font=_font(22, True),
                  fill=(30, 30, 30), anchor="mm")

    # ── 메인 프로그레스 링 (단백질) ──────────────────────────────
    cx, cy = W // 2, 380
    ring_r = 160
    pct_protein = min((protein / protein_goal * 100) if protein_goal > 0 else 0, 100)

    _draw_rounded_rect(draw, [cx - 220, cy - 220, cx + 220, cy + 220], 20, COLOR_CARD)
    _draw_progress_ring(draw, cx, cy, ring_r, pct_protein,
                        (60, 60, 60), COLOR_GREEN, thickness=24)

    draw.text((cx, cy - 30), f"{protein:.0f}g", font=_font(72, True),
              fill=COLOR_GREEN, anchor="mm")
    draw.text((cx, cy + 40), "단백질", font=_font(30),
              fill=COLOR_GRAY, anchor="mm")
    draw.text((cx, cy + 85), f"목표 {protein_goal:.0f}g 의 {pct_protein:.0f}%",
              font=_font(24), fill=COLOR_GRAY, anchor="mm")

    # ── 하단 스탯 3칸 ────────────────────────────────────────────
    pct_cal = min((calories / calorie_goal * 100) if calorie_goal > 0 else 0, 100)
    stats = [
        ("🔥 칼로리", f"{calories:.0f}", "kcal", f"/ {calorie_goal:.0f}", COLOR_GOLD, pct_cal),
        ("🥩 소고기",  f"{beef_g:.0f}",  "g",    "",                       COLOR_RED,  None),
        ("💧 지방",   f"{fat:.1f}",     "g",    "",                       COLOR_GRAY, None),
    ]
    col_w = 320
    start_x = 80
    row_y = 650

    for i, (label, val, unit, sub, color, pct) in enumerate(stats):
        x0 = start_x + i * col_w
        _draw_rounded_rect(draw, [x0, row_y, x0 + 280, row_y + 200], 14, COLOR_CARD)
        draw.text((x0 + 140, row_y + 30), label, font=_font(22),
                  fill=COLOR_GRAY, anchor="mm")
        draw.text((x0 + 140, row_y + 95), val, font=_font(50, True),
                  fill=color, anchor="mm")
        draw.text((x0 + 140, row_y + 130), unit, font=_font(22),
                  fill=COLOR_GRAY, anchor="mm")
        if sub:
            draw.text((x0 + 140, row_y + 158), sub, font=_font(20),
                      fill=COLOR_GRAY, anchor="mm")
        if pct is not None:
            bar_x0, bar_y0 = x0 + 20, row_y + 180
            bar_w = 240
            draw.rectangle([bar_x0, bar_y0, bar_x0 + bar_w, bar_y0 + 8],
                           fill=(60, 60, 60))
            draw.rectangle([bar_x0, bar_y0, bar_x0 + int(bar_w * pct / 100), bar_y0 + 8],
                           fill=color)

    # 체중
    if weight_kg:
        draw.text((W // 2, 900), f"⚖️  오늘 체중  {weight_kg:.1f} kg",
                  font=_font(30, True), fill=COLOR_IVORY, anchor="mm")

    # 브랜드 하단
    draw.rectangle([0, 960, W, 1080], fill=COLOR_CARD)
    draw.text((W // 2, 1020), "#소고기식단 #비프다이어트 #단백질챌린지",
              font=_font(26), fill=COLOR_GRAY, anchor="mm")

    if not is_premium:
        img = _add_watermark(img)

    return img


def create_story_card(
    protein: float, protein_goal: float,
    calories: float, calorie_goal: float,
    fat: float,
    beef_g: float,
    weight_kg: float | None,
    day_str: str,
    is_premium: bool = False,
    challenge_day: int | None = None,
) -> Image.Image:
    """
    인스타그램 스토리/릴스용 1080x1920 카드
    """
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # 상단 레드 배너
    draw.rectangle([0, 0, W, 160], fill=COLOR_RED)
    draw.text((W // 2, 55), "🥩 소고기 식단 트래커", font=_font(52, True),
              fill=COLOR_IVORY, anchor="mm")
    draw.text((W // 2, 120), day_str, font=_font(30),
              fill=COLOR_IVORY, anchor="mm")

    # 챌린지 뱃지
    if challenge_day:
        _draw_rounded_rect(draw, [W // 2 - 160, 180, W // 2 + 160, 240], 10, COLOR_GOLD)
        draw.text((W // 2, 210), f"🏆  50일 챌린지  D+{challenge_day}",
                  font=_font(28, True), fill=(30, 30, 30), anchor="mm")

    # ── 단백질 메인 링 ─────────────────────────────────────────────
    cx, cy = W // 2, 580
    ring_r = 200
    pct_protein = min((protein / protein_goal * 100) if protein_goal > 0 else 0, 100)

    _draw_rounded_rect(draw, [cx - 280, cy - 280, cx + 280, cy + 280], 24, COLOR_CARD)
    _draw_progress_ring(draw, cx, cy, ring_r, pct_protein,
                        (60, 60, 60), COLOR_GREEN, thickness=30)

    draw.text((cx, cy - 50), f"{protein:.0f}g", font=_font(100, True),
              fill=COLOR_GREEN, anchor="mm")
    draw.text((cx, cy + 60), "단백질 섭취", font=_font(36),
              fill=COLOR_GRAY, anchor="mm")
    draw.text((cx, cy + 110), f"목표 {protein_goal:.0f}g 달성률 {pct_protein:.0f}%",
              font=_font(28), fill=COLOR_GRAY, anchor="mm")

    # ── 칼로리 바 ─────────────────────────────────────────────────
    pct_cal = min((calories / calorie_goal * 100) if calorie_goal > 0 else 0, 100)
    _draw_rounded_rect(draw, [60, 920, W - 60, 1060], 16, COLOR_CARD)
    draw.text((100, 945), "🔥 칼로리", font=_font(28), fill=COLOR_GRAY)
    draw.text((W - 100, 945), f"{calories:.0f} / {calorie_goal:.0f} kcal",
              font=_font(28, True), fill=COLOR_GOLD, anchor="ra")
    draw.rectangle([100, 1000, W - 100, 1020], fill=(60, 60, 60))
    bar_end = 100 + int((W - 200) * pct_cal / 100)
    draw.rectangle([100, 1000, bar_end, 1020], fill=COLOR_GOLD)

    # ── 스탯 2칸 ──────────────────────────────────────────────────
    for i, (label, val, unit, color) in enumerate([
        ("🥩 소고기 섭취량", f"{beef_g:.0f}", "g", COLOR_RED),
        ("💧 지방",         f"{fat:.1f}",     "g", COLOR_GRAY),
    ]):
        x0 = 60 + i * 490
        _draw_rounded_rect(draw, [x0, 1100, x0 + 440, 1260], 16, COLOR_CARD)
        draw.text((x0 + 220, 1135), label, font=_font(24), fill=COLOR_GRAY, anchor="mm")
        draw.text((x0 + 220, 1200), val,   font=_font(64, True), fill=color, anchor="mm")
        draw.text((x0 + 220, 1245), unit,  font=_font(26), fill=COLOR_GRAY, anchor="mm")

    # 체중
    if weight_kg:
        _draw_rounded_rect(draw, [60, 1300, W - 60, 1410], 16, COLOR_CARD)
        draw.text((W // 2, 1355), f"⚖️  오늘 체중  {weight_kg:.1f} kg",
                  font=_font(40, True), fill=COLOR_IVORY, anchor="mm")

    # 동기부여 문구
    motivation_lines = [
        ("단백질이 근육을 만든다.", 1480),
        ("오늘도 소고기로 채워라.", 1540),
    ]
    for text, y in motivation_lines:
        draw.text((W // 2, y), text, font=_font(36, True),
                  fill=COLOR_GOLD, anchor="mm")

    # 해시태그
    draw.text((W // 2, 1640), "#소고기식단 #비프다이어트 #단백질챌린지 #헬스낵",
              font=_font(28), fill=COLOR_GRAY, anchor="mm")
    draw.text((W // 2, 1690), "#다이어트식단 #클린이팅 #근성장",
              font=_font(28), fill=COLOR_GRAY, anchor="mm")

    # 브랜드 하단
    draw.rectangle([0, 1820, W, 1920], fill=COLOR_CARD)
    draw.text((W // 2, 1870), "소고기식단 트래커  |  @beeftracker_kr",
              font=_font(30, True), fill=COLOR_GOLD, anchor="mm")

    if not is_premium:
        img = _add_watermark(img)

    return img
