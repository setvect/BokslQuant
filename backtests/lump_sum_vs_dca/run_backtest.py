#!/usr/bin/env python3
"""
일시투자 vs 적립투자 백테스팅 실행 스크립트
"""
import sys
import os

# 현재 디렉토리를 src로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# 실행
if __name__ == "__main__":
    from main import main
    sys.exit(main())