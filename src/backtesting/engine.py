"""
백테스팅 엔진 모듈
데이터 로드 전용 엔진
"""
import pandas as pd
import numpy as np
from typing import Dict
import os


class InvestmentBacktester:
    """데이터 로드 전용 백테스팅 엔진"""
    
    def __init__(self, data_path: str = "data/"):
        """
        백테스터 초기화
        
        Args:
            data_path: 데이터 파일 경로
        """
        self.data_path = data_path
        self.available_indices = self._scan_available_data()
    
    def _scan_available_data(self) -> Dict[str, str]:
        """사용 가능한 데이터 파일 스캔"""
        available_data = {}
        
        if not os.path.exists(self.data_path):
            return available_data
        
        # CSV 파일들을 스캔하여 지수명 추출
        for filename in os.listdir(self.data_path):
            if filename.endswith('.csv'):
                index_name = filename.replace('_data.csv', '').replace('.csv', '')
                available_data[index_name.upper()] = os.path.join(self.data_path, filename)
        
        return available_data
    
    def load_data(self, index_name: str) -> pd.DataFrame:
        """
        지정된 지수 데이터 로드
        
        Args:
            index_name: 지수명 (예: 'SP500', 'KOSPI')
        
        Returns:
            가격 데이터 DataFrame
        """
        index_name = index_name.upper()
        
        if index_name not in self.available_indices:
            raise ValueError(f"'{index_name}' 데이터를 찾을 수 없습니다. "
                           f"사용 가능한 지수: {list(self.available_indices.keys())}")
        
        file_path = self.available_indices[index_name]
        
        try:
            df = pd.read_csv(file_path)
            
            # 날짜 컬럼을 인덱스로 설정
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], utc=True)
                df.set_index('Date', inplace=True)
            
            # 필요한 컬럼들이 있는지 확인
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_columns}")
            
            # 결측치 처리
            df = df.dropna()
            
            # 날짜순 정렬
            df = df.sort_index()
            
            return df
        
        except Exception as e:
            raise ValueError(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
    
    def get_available_indices(self) -> list:
        """사용 가능한 지수 목록 반환"""
        return list(self.available_indices.keys())