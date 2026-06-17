BEEF_PRODUCTS = [
    # (부위, 형태, 칼로리/100g, 단백질g/100g, 지방g/100g)
    ("부채살", "통스테이크", 150, 21.5, 6.6),
    ("부채살", "슬라이스",   150, 21.5, 6.6),
    ("부채살", "큐브스테이크", 150, 21.5, 6.6),
    ("우둔살", "통스테이크", 155, 23.1, 7.3),
    ("우둔살", "슬라이스",   155, 23.1, 7.3),
    ("우둔살", "큐브스테이크", 155, 23.1, 7.3),
    ("홍두깨살", "통스테이크", 127, 23.2, 3.8),
    ("홍두깨살", "슬라이스",   127, 23.2, 3.8),
    ("홍두깨살", "큐브스테이크", 127, 23.2, 3.8),
    ("지방제한 다짐육", "-", 129, 22.9, 4.1),
]

PACK_SIZES = [100, 200]

def get_nutrition(부위: str, 형태: str, 중량g: int) -> dict:
    for p in BEEF_PRODUCTS:
        if p[0] == 부위 and p[1] == 형태:
            ratio = 중량g / 100
            return {
                "칼로리": round(p[2] * ratio, 1),
                "단백질": round(p[3] * ratio, 1),
                "지방":   round(p[4] * ratio, 1),
            }
    return {"칼로리": 0, "단백질": 0, "지방": 0}

def get_cuts() -> list[str]:
    return list(dict.fromkeys(p[0] for p in BEEF_PRODUCTS))

def get_types(부위: str) -> list[str]:
    return [p[1] for p in BEEF_PRODUCTS if p[0] == 부위]
