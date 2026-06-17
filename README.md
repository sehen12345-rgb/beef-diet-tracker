# 소고기 식단 트래커 🥩

## 개요
호주산 소고기 전문 식단 관리 앱. 부채살·우둔살·홍두깨살·지방제한 다짐육 기반으로 일일 단백질·칼로리·지방을 추적하고, 체중 변화를 시각화한다.

---

## 개발 환경

| 항목 | 내용 |
|------|------|
| Language | Python 3.11+ |
| GUI | PyQt5 |
| 데이터 저장 | SQLite (로컬) |
| 차트 | matplotlib |
| OS | Windows 10/11 |

### 설치 방법
```bash
# 1. Python 설치 (https://www.python.org/downloads/)
#    ※ 반드시 "Add Python to PATH" 체크

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 실행
python main.py
```

---

## 아키텍처

```
beef-diet-tracker/
├── main.py              # 앱 진입점
├── ui/
│   ├── main_window.py   # 메인 윈도우
│   ├── dashboard.py     # 오늘의 요약 탭
│   ├── food_log.py      # 식단 기록 탭
│   ├── weight_log.py    # 체중 기록 탭
│   └── report.py        # 주간 리포트 탭
├── data/
│   ├── database.py      # SQLite CRUD
│   ├── beef_db.py       # 소고기 영양성분 DB
│   └── tracker.db       # 실제 데이터 파일 (자동생성)
├── requirements.txt
└── README.md
```

---

## 영양성분 DB (호주산 기준, 100g 생것)

| 부위 | 형태 | 칼로리 | 단백질 | 지방 |
|------|------|--------|--------|------|
| 부채살 | 통스테이크 | 150kcal | 21.5g | 6.6g |
| 부채살 | 슬라이스 | 150kcal | 21.5g | 6.6g |
| 부채살 | 큐브스테이크 | 150kcal | 21.5g | 6.6g |
| 우둔살 | 통스테이크 | 155kcal | 23.1g | 7.3g |
| 우둔살 | 슬라이스 | 155kcal | 23.1g | 7.3g |
| 우둔살 | 큐브스테이크 | 155kcal | 23.1g | 7.3g |
| 홍두깨살 | 통스테이크 | 127kcal | 23.2g | 3.8g |
| 홍두깨살 | 슬라이스 | 127kcal | 23.2g | 3.8g |
| 홍두깨살 | 큐브스테이크 | 127kcal | 23.2g | 3.8g |
| 지방제한 다짐육 | — | 129kcal | 22.9g | 4.1g |

> 출처: 농촌진흥청 국가표준식품성분표 + MLA(Meat & Livestock Australia) 공식 연구자료

---

## 디자인 가이드

### 컬러 팔레트
| 역할 | 색상 | HEX |
|------|------|-----|
| 메인 (소고기 레드) | 딥 레드 | `#8B1A1A` |
| 서브 (크림) | 아이보리 | `#FAF3E0` |
| 강조 (골드) | 골드 | `#C9A84C` |
| 배경 | 다크 차콜 | `#1E1E1E` |
| 텍스트 | 화이트 | `#F5F5F5` |
| 성공/달성 | 그린 | `#4CAF50` |
| 경고/초과 | 오렌지 | `#FF6B35` |

### 폰트
- 제목: Pretendard Bold 18px
- 본문: Pretendard Regular 13px
- 숫자/수치: Pretendard Medium 15px (모노스페이스 느낌)

### UI 원칙
- 다크 테마 기본 (헬스/다이어트 앱 트렌드)
- 카드형 레이아웃
- 진행률 바로 목표 달성도 시각화
- 최소 클릭으로 빠른 기록 가능

---

## 배포 환경

| 항목 | 내용 |
|------|------|
| 배포 형태 | Windows .exe (PyInstaller) |
| 판매 플랫폼 | litt.ly 결제 → 구글드라이브 다운로드 링크 |
| 가격 (예정) | 9,900원 ~ 14,900원 |
| 업데이트 | 수동 (버전별 재배포) |

### exe 빌드 방법
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "소고기식단트래커" main.py
# dist/ 폴더에 .exe 생성
```

---

## TODO 리스트

### ✅ 완료
- [x] 프로젝트 구조 설계
- [x] 영양성분 DB 설계
- [x] README 문서화
- [x] 디자인 가이드 수립

### 🔄 개발 중
- [ ] SQLite 데이터베이스 설계
- [ ] 소고기 영양성분 DB 코드 작성
- [ ] 메인 윈도우 UI
- [ ] 식단 기록 탭
- [ ] 체중 기록 탭
- [ ] 오늘의 요약 대시보드

### 📋 추가 예정
- [ ] 주간 리포트 + 그래프
- [ ] 목표 설정 기능
- [ ] 데이터 CSV 내보내기
- [ ] exe 패키징
- [ ] litt.ly 판매 페이지 연동
