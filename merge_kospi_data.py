#!/usr/bin/env python3
"""
KOSPI 데이터 병합 프로그램

temp_investing 디렉토리의 3개 CSV 파일을 병합하여 
기존 KOSPI_data.csv 형식에 맞게 변환합니다.
"""

import csv
import os
from datetime import datetime

def convert_korean_date(date_str):
    """한국어 날짜 형식을 영어 형식으로 변환"""
    # "1998- 05- 20" -> "1998-05-20"
    return date_str.strip().replace('- ', '-').replace(' -', '-')

def parse_volume(volume_str):
    """거래량 문자열을 숫자로 변환 (M 단위 처리)"""
    if isinstance(volume_str, str):
        volume_str = volume_str.strip()
        if volume_str.endswith('M'):
            return str(float(volume_str[:-1]) * 1_000_000)
    try:
        return str(float(volume_str))
    except:
        return '0'

def parse_price(price_str):
    """가격 문자열을 숫자로 변환 (쉼표 제거)"""
    if isinstance(price_str, str):
        return str(float(price_str.replace(',', '')))
    return str(float(price_str))

def remove_non_trading_days(data_list):
    """휴장일 제거 - 전날과 동일한 가격 데이터 제거"""
    if len(data_list) <= 1:
        return data_list
    
    filtered_data = [data_list[0]]  # 첫 번째 데이터는 항상 포함
    removed_count = 0
    
    for i in range(1, len(data_list)):
        current = data_list[i]
        previous = data_list[i-1]
        
        # 전날과 모든 가격이 동일한지 확인 (Open, High, Low, Close)
        if (current['Open'] == previous['Open'] and 
            current['High'] == previous['High'] and 
            current['Low'] == previous['Low'] and 
            current['Close'] == previous['Close']):
            removed_count += 1
            print(f"  - 휴장일 제거: {current['Date']} (전날과 동일한 가격)")
            continue
        
        filtered_data.append(current)
    
    print(f"  - 총 {removed_count}개의 휴장일 데이터 제거됨")
    return filtered_data

def merge_kospi_data():
    """KOSPI 데이터 병합 및 변환"""
    
    # 파일 경로 설정
    temp_dir = "temp/investing"
    output_file = "data/KOSPI_data_temp.csv"
    
    # 기존 KOSPI 파일 읽기
    existing_data = []
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_data.append(row)
    except FileNotFoundError:
        print(f"기존 파일을 찾을 수 없습니다: {output_file}")
        print("새로운 파일을 생성합니다.")
    
    print(f"기존 KOSPI 데이터: {len(existing_data)} rows")
    if existing_data:
        print(f"기존 데이터 컬럼: {list(existing_data[0].keys())}")
        dates = [row['Date'] for row in existing_data]
        print(f"기존 데이터 기간: {min(dates)} ~ {max(dates)}")
    
    # 병합할 데이터를 저장할 리스트
    all_data = existing_data.copy()
    existing_dates = set(row['Date'] for row in existing_data)
    
    # temp_investing 디렉토리의 모든 CSV 파일 처리
    if not os.path.exists(temp_dir):
        print(f"\n경고: {temp_dir} 디렉토리를 찾을 수 없습니다.")
        print("병합할 새 데이터가 없으므로 기존 데이터에서 휴장일만 제거합니다.")
        csv_files = []
    else:
        csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
        print(f"\n처리할 파일들: {csv_files}")
    
    new_count = 0
    for csv_file in csv_files:
        file_path = os.path.join(temp_dir, csv_file)
        print(f"\n처리 중: {csv_file}")
        
        # CSV 파일 읽기
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        print(f"  - 원본 데이터: {len(rows)} rows")
        print(f"  - 컬럼: {list(rows[0].keys()) if rows else 'None'}")
        
        # 데이터 변환
        for row in rows:
            try:
                # 날짜 변환
                date_str = convert_korean_date(str(row['날짜']))
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S+09:00')
                
                # 중복 체크
                if formatted_date in existing_dates:
                    continue
                
                # 기존 KOSPI 형식에 맞게 데이터 변환
                converted_row = {
                    'Date': formatted_date,
                    'Open': parse_price(row['시가']),
                    'High': parse_price(row['고가']),
                    'Low': parse_price(row['저가']),
                    'Close': parse_price(row['종가']),
                    'Volume': parse_volume(row['거래량']),
                    'Dividends': '0.0',
                    'Stock Splits': '0.0'
                }
                all_data.append(converted_row)
                existing_dates.add(formatted_date)
                new_count += 1
                
            except Exception as e:
                print(f"  - 변환 오류 (행 건너뜀): {e}")
                continue
        
        print(f"  - 새로 추가된 데이터: {new_count} rows")
    
    # 데이터가 있으면 휴장일 제거 및 처리
    if all_data:
        print(f"\n휴장일 제거 전: {len(all_data)} rows")
        
        # 날짜 기준 정렬
        all_data.sort(key=lambda x: datetime.strptime(x['Date'][:19], '%Y-%m-%d %H:%M:%S'))
        
        # 휴장일 제거
        all_data = remove_non_trading_days(all_data)
        print(f"휴장일 제거 후: {len(all_data)} rows")
        
        # 새 파일 저장
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if all_data:
                writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
                writer.writeheader()
                writer.writerows(all_data)
        
        print(f"병합 완료: {output_file}")
        print(f"최종 데이터: {len(all_data)} rows")
        if new_count > 0:
            print(f"새로 추가된 데이터: {new_count} rows")
        
        dates = [row['Date'] for row in all_data]
        print(f"데이터 기간: {min(dates)} ~ {max(dates)}")
        
    else:
        print("처리할 데이터가 없습니다.")

if __name__ == "__main__":
    merge_kospi_data()