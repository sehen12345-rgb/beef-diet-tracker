"""
판매자 전용 라이선스 키 생성 스크립트
사용법: python generate_key.py 구매자이메일@example.com
"""
import sys
from data.license import generate_key_for_email

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python generate_key.py 구매자이메일@example.com")
        sys.exit(1)
    email = sys.argv[1].strip()
    key = generate_key_for_email(email)
    print(f"\n이메일: {email}")
    print(f"라이선스 키: {key}")
    print("\n위 키를 구매자에게 전달하세요.")
