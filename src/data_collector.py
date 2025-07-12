#!/usr/bin/env python3
"""
주식 지수 데이터 수집 모듈

주요 기능:
- 나스닥, S&P 500, 코스피 등 주요 지수의 일봉 데이터 수집
- 전기간 데이터 수집 (가능한 모든 기간)
- 명령행 인수를 통한 수집 대상 지정
- 데이터 캐싱 및 저장

사용법:
    python src/data_collector.py --indices NASDAQ SP500 KOSPI
    python src/data_collector.py --all
    python src/data_collector.py --help
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import yfinance as yf
import requests
from pathlib import Path


class IndexDataCollector:
    """주식 지수 데이터 수집기"""
    
    # 지원하는 지수 목록 (예상 시작일 포함)
    SUPPORTED_INDICES = {
        'NASDAQ': {'symbol': '^IXIC', 'expected_start': '1971-02-05'},      # 나스닥 종합지수
        'SP500': {'symbol': '^GSPC', 'expected_start': '1957-03-04'},       # S&P 500 (실제 500개 기업 시작)
        'DOW': {'symbol': '^DJI', 'expected_start': '1896-05-26'},          # 다우존스
        'KOSPI': {'symbol': '^KS11', 'expected_start': '1980-01-04'},       # 코스피 ⚠️ 데이터 누락
        'KOSDAQ': {'symbol': '^KQ11', 'expected_start': '1996-07-01'},      # 코스닥
        'NIKKEI': {'symbol': '^N225', 'expected_start': '1950-09-07'},      # 니케이 225
        'FTSE': {'symbol': '^FTSE', 'expected_start': '1984-01-03'},        # FTSE 100
        'DAX': {'symbol': '^GDAXI', 'expected_start': '1959-12-31'},        # DAX
        'CAC': {'symbol': '^FCHI', 'expected_start': '1987-12-31'},         # CAC 40
        'HSI': {'symbol': '^HSI', 'expected_start': '1964-07-31'},          # 항셍지수
    }
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: 데이터 저장 디렉토리
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 캐시 디렉토리 생성
        self.cache_dir = self.data_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_available_indices(self) -> Dict[str, dict]:
        """사용 가능한 지수 목록 반환"""
        return self.SUPPORTED_INDICES.copy()
    
    def validate_indices(self, indices: List[str]) -> List[str]:
        """지수 이름 검증 및 정규화"""
        valid_indices = []
        for index in indices:
            index_upper = index.upper()
            if index_upper in self.SUPPORTED_INDICES:
                valid_indices.append(index_upper)
            else:
                print(f"Warning: '{index}' is not a supported index. Skipping...")
                print(f"Supported indices: {', '.join(self.SUPPORTED_INDICES.keys())}")
        return valid_indices
    
    def collect_index_data(self, index_name: str, period: str = "max") -> Optional[pd.DataFrame]:
        """
        지수 데이터 수집
        
        Args:
            index_name: 지수 이름 (예: 'NASDAQ', 'SP500')
            period: 데이터 수집 기간 ('max' for 전체 기간)
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        if index_name not in self.SUPPORTED_INDICES:
            print(f"Error: Unsupported index '{index_name}'")
            return None
            
        symbol = self.SUPPORTED_INDICES[index_name]['symbol']
        expected_start = pd.to_datetime(self.SUPPORTED_INDICES[index_name]['expected_start'])
        
        try:
            print(f"Collecting data for {index_name} ({symbol})...")
            
            # yfinance를 사용하여 데이터 수집
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval="1d")
            
            if data.empty:
                print(f"Warning: No data found for {index_name}")
                return None
            
            # S&P 500의 경우 1957년 이후 데이터만 필터링
            if index_name == 'SP500':
                original_count = len(data)
                # 타임존을 고려한 필터링
                if data.index.tz is not None:
                    expected_start = expected_start.tz_localize(data.index.tz)
                data = data[data.index >= expected_start]
                filtered_count = len(data)
                print(f"  📅 S&P 500: 1957년 이후 데이터로 필터링 ({original_count} → {filtered_count} days)")
                
            # 컬럼명 정리
            data.index.name = 'Date'
            data = data.round(2)  # 소수점 2자리로 반올림
            
            # 데이터 완성도 검증
            expected_start = pd.to_datetime(self.SUPPORTED_INDICES[index_name]['expected_start']).date()
            actual_start = data.index[0].date()
            actual_end = data.index[-1].date()
            
            print(f"✓ {index_name}: {len(data)} days of data collected")
            print(f"  Period: {actual_start} to {actual_end}")
            
            # 누락 데이터 경고
            if actual_start > expected_start:
                missing_days = (actual_start - expected_start).days
                missing_years = round(missing_days / 365.25, 1)
                print(f"  ⚠️  Warning: {missing_years} years of data missing from expected start ({expected_start})")
                if index_name in ['KOSPI', 'KOSDAQ']:
                    print(f"     💡 Tip: Use 'python src/korea_data_collector.py --indices {index_name}' for better Korea data")
            
            return data
            
        except Exception as e:
            print(f"Error collecting data for {index_name}: {str(e)}")
            return None
    
    def save_data(self, data: pd.DataFrame, index_name: str) -> str:
        """
        데이터를 CSV 파일로 저장
        
        Args:
            data: 저장할 데이터
            index_name: 지수 이름
            
        Returns:
            저장된 파일 경로
        """
        filename = f"{index_name}_data.csv"
        filepath = self.data_dir / filename
        
        # 기존 데이터와 병합 (있는 경우)
        if filepath.exists():
            try:
                existing_data = pd.read_csv(filepath, index_col=0, parse_dates=True)
                # 중복 제거하고 병합
                combined_data = pd.concat([existing_data, data])
                combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
                combined_data = combined_data.sort_index()
                data = combined_data
                print(f"  Updated existing data for {index_name}")
            except Exception as e:
                print(f"  Warning: Could not merge with existing data: {e}")
        
        data.to_csv(filepath)
        print(f"  Saved to: {filepath}")
        return str(filepath)
    
    def collect_multiple_indices(self, indices: List[str]) -> Dict[str, str]:
        """
        여러 지수의 데이터를 일괄 수집
        
        Args:
            indices: 수집할 지수 이름 목록
            
        Returns:
            {index_name: filepath} 딕셔너리
        """
        results = {}
        valid_indices = self.validate_indices(indices)
        
        if not valid_indices:
            print("No valid indices to collect.")
            return results
        
        print(f"\nStarting data collection for {len(valid_indices)} indices...")
        print("=" * 60)
        
        for i, index_name in enumerate(valid_indices, 1):
            print(f"\n[{i}/{len(valid_indices)}] Processing {index_name}...")
            
            data = self.collect_index_data(index_name)
            if data is not None:
                filepath = self.save_data(data, index_name)
                results[index_name] = filepath
            else:
                print(f"  Failed to collect data for {index_name}")
        
        return results
    
    def get_summary(self) -> pd.DataFrame:
        """저장된 데이터 파일들의 요약 정보 반환"""
        summary_data = []
        
        for index_name, info in self.SUPPORTED_INDICES.items():
            filepath = self.data_dir / f"{index_name}_data.csv"
            if filepath.exists():
                try:
                    data = pd.read_csv(filepath, index_col=0, parse_dates=True)
                    expected_start = pd.to_datetime(info['expected_start']).date()
                    actual_start = data.index.min().date()
                    
                    # 누락 연수 계산
                    missing_years = 0
                    if actual_start > expected_start:
                        missing_days = (actual_start - expected_start).days
                        missing_years = round(missing_days / 365.25, 1)
                    
                    summary_data.append({
                        'Index': index_name,
                        'Symbol': info['symbol'],
                        'Records': len(data),
                        'Start_Date': actual_start,
                        'End_Date': data.index.max().date(),
                        'Expected_Start': expected_start,
                        'Missing_Years': missing_years,
                        'File_Size_MB': round(filepath.stat().st_size / 1024 / 1024, 2)
                    })
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
        
        return pd.DataFrame(summary_data)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="주식 지수 데이터 수집기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s --indices NASDAQ SP500 KOSPI    # 특정 지수들 수집
  %(prog)s --all                          # 모든 지수 수집
  %(prog)s --list                         # 지원하는 지수 목록 출력
  %(prog)s --summary                      # 저장된 데이터 요약 출력
        """
    )
    
    parser.add_argument(
        '--indices', 
        nargs='+', 
        help='수집할 지수 이름들 (예: NASDAQ SP500 KOSPI)'
    )
    
    parser.add_argument(
        '--all', 
        action='store_true',
        help='모든 지원하는 지수 데이터 수집'
    )
    
    parser.add_argument(
        '--list', 
        action='store_true',
        help='지원하는 지수 목록 출력'
    )
    
    parser.add_argument(
        '--summary', 
        action='store_true',
        help='저장된 데이터 파일 요약 정보 출력'
    )
    
    parser.add_argument(
        '--data-dir', 
        default='data',
        help='데이터 저장 디렉토리 (기본값: data)'
    )
    
    args = parser.parse_args()
    
    # 데이터 수집기 초기화
    collector = IndexDataCollector(args.data_dir)
    
    # 지원하는 지수 목록 출력
    if args.list:
        print("지원하는 주식 지수:")
        print("=" * 60)
        for name, info in collector.get_available_indices().items():
            missing_note = " ⚠️ 데이터 누락" if name in ['KOSPI', 'KOSDAQ'] else ""
            print(f"  {name:<10} : {info['symbol']} (예상시작: {info['expected_start']}){missing_note}")
        return
    
    # 저장된 데이터 요약 출력
    if args.summary:
        print("저장된 데이터 요약:")
        print("=" * 60)
        summary = collector.get_summary()
        if not summary.empty:
            print(summary.to_string(index=False))
        else:
            print("저장된 데이터가 없습니다.")
        return
    
    # 데이터 수집 실행
    if args.all:
        # 모든 지수 수집
        indices = list(collector.get_available_indices().keys())
        print(f"모든 지수 데이터를 수집합니다: {', '.join(indices)}")
    elif args.indices:
        # 지정된 지수들 수집
        indices = args.indices
    else:
        # 인수가 없으면 도움말 출력
        parser.print_help()
        return
    
    # 수집 시작
    start_time = datetime.now()
    results = collector.collect_multiple_indices(indices)
    end_time = datetime.now()
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("수집 완료!")
    print(f"소요 시간: {end_time - start_time}")
    print(f"성공: {len(results)}/{len(indices)} 지수")
    
    if results:
        print("\n저장된 파일:")
        for index_name, filepath in results.items():
            print(f"  {index_name}: {filepath}")
    
    # 최종 요약 출력
    summary = collector.get_summary()
    if not summary.empty:
        print(f"\n전체 데이터 현황:")
        print(f"총 {len(summary)}개 지수, {summary['Records'].sum():,}개 레코드")


if __name__ == "__main__":
    main()