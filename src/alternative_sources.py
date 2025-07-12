#!/usr/bin/env python3
"""
대체 데이터 소스 테스트 모듈

yfinance 외의 다른 데이터 소스들을 테스트하여
1980년부터의 코스피 데이터를 찾아봅니다.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json


def test_fred_api():
    """
    FRED (Federal Reserve Economic Data) API 테스트
    한국 데이터가 있는지 확인
    """
    print("🔍 FRED API 테스트...")
    
    # FRED API는 무료이지만 API 키가 필요
    # 여기서는 공개 검색만 테스트
    try:
        search_url = "https://api.stlouisfed.org/fred/series/search"
        params = {
            'search_text': 'korea kospi',
            'api_key': 'demo',  # 실제 사용시 API 키 필요
            'file_type': 'json'
        }
        
        # 실제 API 키 없이는 작동하지 않지만 구조 확인
        print(f"  FRED 검색 URL: {search_url}")
        print(f"  검색어: korea kospi")
        print(f"  ❌ API 키가 필요하여 실제 테스트 불가")
        return False
        
    except Exception as e:
        print(f"  ❌ FRED API 오류: {e}")
        return False


def test_quandl_sources():
    """
    Quandl/Nasdaq Data Link 테스트
    """
    print("\n🔍 Quandl 데이터 소스 테스트...")
    
    # Quandl도 API 키가 필요하지만 일부 공개 데이터 존재
    try:
        # 예시 URL들 (실제 작동 여부 확인)
        sources = [
            "https://www.quandl.com/api/v3/datasets/NASDAQOMX/KOSPI.json",
            "https://data.nasdaq.com/api/v3/datasets/KOREA/KOSPI.json"
        ]
        
        for url in sources:
            print(f"  테스트 URL: {url}")
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ 응답 성공! 크기: {len(response.content)} bytes")
                    return True
                else:
                    print(f"  ❌ HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ 연결 실패: {str(e)[:50]}")
        
        return False
        
    except Exception as e:
        print(f"  ❌ Quandl 테스트 오류: {e}")
        return False


def test_yahoo_alternative_symbols():
    """
    Yahoo Finance에서 다른 한국 심볼들 테스트
    """
    print("\n🔍 Yahoo Finance 대체 심볼 테스트...")
    
    import yfinance as yf
    
    # 시도해볼 다양한 심볼들
    symbols = [
        "180640.KS",  # 한국투자증권 KOSPI 200 ETF
        "069500.KS",  # KODEX 200
        "102110.KS",  # KODEX Bank
        "KS11.KS",    # 다른 형태
        "000001.KS",  # 다른 시도
    ]
    
    results = []
    
    for symbol in symbols:
        try:
            print(f"  테스트 심볼: {symbol}")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="max")
            
            if not data.empty:
                start_date = data.index[0].date()
                end_date = data.index[-1].date()
                days = len(data)
                print(f"    ✅ 성공: {days} days ({start_date} ~ {end_date})")
                
                results.append({
                    'symbol': symbol,
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': days
                })
            else:
                print(f"    ❌ 데이터 없음")
                
        except Exception as e:
            print(f"    ❌ 오류: {str(e)[:50]}")
    
    return results


def test_alpha_vantage():
    """
    Alpha Vantage API 테스트 (무료 tier 존재)
    """
    print("\n🔍 Alpha Vantage API 테스트...")
    
    try:
        # Alpha Vantage는 무료 API 키 제공
        # demo 키로 테스트 가능
        api_key = "demo"
        base_url = "https://www.alphavantage.co/query"
        
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': 'KOSPI',  # 지원하는지 확인
            'apikey': api_key,
            'outputsize': 'full'
        }
        
        print(f"  Alpha Vantage URL: {base_url}")
        print(f"  심볼: KOSPI")
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'Time Series (Daily)' in data:
                print(f"  ✅ 성공! 데이터 키 발견")
                dates = list(data['Time Series (Daily)'].keys())
                earliest = min(dates)
                latest = max(dates)
                print(f"  📅 기간: {earliest} ~ {latest}")
                return True
            else:
                print(f"  ❌ 데이터 형식 다름: {list(data.keys())}")
        else:
            print(f"  ❌ HTTP {response.status_code}")
            
        return False
        
    except Exception as e:
        print(f"  ❌ Alpha Vantage 오류: {e}")
        return False


def test_investing_com_direct():
    """
    investing.com에서 직접 데이터 요청 테스트
    """
    print("\n🔍 Investing.com 직접 요청 테스트...")
    
    try:
        # investing.com의 실제 API 엔드포인트 추정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.investing.com/indices/kospi-historical-data'
        }
        
        # 몇 가지 가능한 API URL 시도
        api_urls = [
            "https://api.investing.com/api/financialdata/historical/180",  # KOSPI ID 추정
            "https://tvc4.investing.com/api/search/stocks?text=kospi",
            "https://www.investing.com/instruments/HistoricalDataAjax"
        ]
        
        for url in api_urls:
            print(f"  테스트 URL: {url}")
            try:
                response = requests.get(url, headers=headers, timeout=5)
                print(f"    상태: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    print(f"    내용 미리보기: {content}")
                    
                    # JSON 파싱 시도
                    try:
                        data = response.json()
                        print(f"    ✅ JSON 파싱 성공: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                    except:
                        print(f"    📄 텍스트 응답 (JSON 아님)")
                        
            except Exception as e:
                print(f"    ❌ 요청 실패: {str(e)[:50]}")
        
        return False
        
    except Exception as e:
        print(f"  ❌ Investing.com 테스트 오류: {e}")
        return False


def main():
    """모든 대체 데이터 소스 테스트"""
    print("=" * 80)
    print("🔍 대체 데이터 소스 탐색")
    print("목표: 1980년부터의 코스피 데이터 찾기")
    print("=" * 80)
    
    results = []
    
    # 1. Yahoo Finance 대체 심볼들
    yahoo_results = test_yahoo_alternative_symbols()
    if yahoo_results:
        results.extend(yahoo_results)
    
    # 2. FRED API
    fred_success = test_fred_api()
    
    # 3. Quandl
    quandl_success = test_quandl_sources()
    
    # 4. Alpha Vantage
    alpha_success = test_alpha_vantage()
    
    # 5. Investing.com 직접
    investing_success = test_investing_com_direct()
    
    # 결과 요약
    print("\n" + "=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    
    if yahoo_results:
        print(f"\n✅ Yahoo Finance 대체 심볼 발견: {len(yahoo_results)}개")
        for result in yahoo_results:
            print(f"  - {result['symbol']}: {result['start_date']} ~ {result['end_date']} ({result['days']} days)")
    
    success_count = sum([
        len(yahoo_results) > 0,
        fred_success,
        quandl_success, 
        alpha_success,
        investing_success
    ])
    
    print(f"\n📈 총 {success_count}/5 개 소스에서 데이터 발견")
    
    if success_count == 0:
        print("\n💡 권장사항:")
        print("1. KRX (한국거래소) 공식 웹사이트에서 수동 다운로드")
        print("2. 한국은행 ECOS 시스템 활용")
        print("3. 금융 데이터 제공업체 API 구독 (Bloomberg, Refinitiv 등)")
        print("4. 학술/연구 목적 데이터 요청")
    
    return results


if __name__ == "__main__":
    main()