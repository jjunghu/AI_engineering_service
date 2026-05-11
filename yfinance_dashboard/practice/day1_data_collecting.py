# 필수 설치 패키지
# pip install yfinance streamlit plotly pandas pyupbit

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# yfinance API 탐색
# ticker = yf.Ticker('AAPL')

# info: 종목의 다양한 정보가 담긴 딕셔너리
# info = ticker.info
# print('=== 사용 가능한 키 목록 (일부) ===')
# keys_to_show = ['currentPrice', 'previousClose', 'shortName', 'currency', 'marketCap']
# for key in keys_to_show:
#     print(f'  {key}: {info.get(key)}')

# === 사용 가능한 키 목록 (일부) ===
#   currentPrice: 293.257
#   previousClose: 287.486
#   shortName: Apple Inc.
#   currency: USD
#   marketCap: 4307169837056
#####################################################################################################
#  히스토리 데이터 구조 확인
# hist = ticker.history(period='1mo')  # 최근 1달

# print('=== DataFrame 컬럼 ===')
# print(hist.columns.tolist())
# print()
# print('=== 최근 5일 데이터 ===')
# print(hist.tail())
# print()
# print(f'행 수: {len(hist)}, 컬럼 수: {len(hist.columns)}')

# === DataFrame 컬럼 ===
# ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']

# === 최근 5일 데이터 ===
#                                  Open        High         Low       Close    Volume  Dividends  Stock Splits
# Date                                                                                                        
# 2026-05-04 00:00:00-04:00  279.660004  280.630005  274.859985  276.829987  46668400        0.0           0.0
# 2026-05-05 00:00:00-04:00  276.929993  284.570007  276.500000  284.179993  49311700        0.0           0.0
# 2026-05-06 00:00:00-04:00  281.920013  288.029999  281.070007  287.510010  58336100        0.0           0.0
# 2026-05-07 00:00:00-04:00  289.269989  292.130005  285.779999  287.440002  45224300        0.0           0.0
# 2026-05-08 00:00:00-04:00  290.010010  294.760010  290.000000  293.320007  52631200        0.0           0.0

# 행 수: 22, 컬럼 수: 7

###############################################################################################################
# period 옵션 종류 확인
# period 값: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y'

# for period in ['1wk', '1mo', '3mo', '1y']:
#     df = ticker.history(period=period)
#     print(f'period={period!r:8s} → {len(df):3d}행,  기간: {df.index[0].date()} ~ {df.index[-1].date()}')

# period='1wk'    →   5행,  기간: 2026-05-04 ~ 2026-05-08
# period='1mo'    →  22행,  기간: 2026-04-09 ~ 2026-05-08
# period='3mo'    →  63행,  기간: 2026-02-09 ~ 2026-05-08
# period='1y'     → 251행,  기간: 2025-05-09 ~ 2026-05-08

############################################################################################################

# 종목 현재 정보 조회 함수
def get_stock_info(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        result = {
            'name'         : info.get('shortName', ticker_symbol),
            'current_price': info.get('currentPrice', 0),
            'prev_close'   : info.get('previousClose', 0),
            'currency'     : info.get('currency', 'USD')
        }

        if result['current_price'] == 0:
            print(f'[경고] {ticker_symbol}: 가격 데이터를 찾을 수 없습니다.')
            return None
        
        return result
    
    except Exception as e:
        print(f'[오류] {ticker_symbol}: {e}')
        return None
    
#-------------------------------------------------------------------
# 함수 테스트
# print('=== 정상 케이스 ===')
# result = get_stock_info('AAPL')
# print(result)

# print()
# print('=== 한국 주식 ===')
# result_kr = get_stock_info('005930.KS')  # 삼성전자
# print(result_kr)

# print()
# print('=== 오류 케이스 (잘못된 티커) ===')
# result_err = get_stock_info('INVALID_TICKER_XYZ')
# print(result_err)  # None이 출력되어야 함

# === 정상 케이스 ===
# {'name': 'Apple Inc.', 'current_price': 293.257, 'prev_close': 287.486, 'currency': 'USD'}

# === 한국 주식 ===
# {'name': 'SamsungElec', 'current_price': 285500.0, 'prev_close': 268500.0, 'currency': 'KRW'}

# === 오류 케이스 (잘못된 티커) ===
# HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: INVALID_TICKER_XYZ"}}}
# [경고] INVALID_TICKER_XYZ: 가격 데이터를 찾을 수 없습니다.
# None

# =================================================================================
# 기간별 가격 히스토리 함수
def get_stock_history(ticker_symbol, period='1달'):
    period_map = {
        '1주': '1wk',
        '1달': '1mo',
        '3달': '3mo',
        '1년': '1y'
    }

    yf_period = period_map.get(period, '1mo')

    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=yf_period)

        if df.empty:
            print(f'[경고] {ticker_symbol}: 히스토리 데이터가 없습니다.')
            return None
        
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    except Exception as e:
        print(f'[오류] {ticker_symbol} 히스토리 조회 실패: {e}')
        return None
    

#-----------------------------------------------------------------
# 함수 테스트
# df = get_stock_history('AAPL', '1달')
# print(f'행 수: {len(df)}')
# print(df.tail(3))

# print()
# # 여러 기간 테스트
# for period in ['1주', '1달', '3달', '1년']:
#     df = get_stock_history('TSLA', period)
#     print(f'기간={period} → {len(df)}행')

# 행 수: 22
#                                  Open        High         Low       Close    Volume
# Date                                                                               
# 2026-05-06 00:00:00-04:00  281.920013  288.029999  281.070007  287.510010  58336100
# 2026-05-07 00:00:00-04:00  289.269989  292.130005  285.779999  287.440002  45224300
# 2026-05-08 00:00:00-04:00  290.010010  294.760010  290.000000  293.320007  52631200

# 기간=1주 → 5행
# 기간=1달 → 22행
# 기간=3달 → 63행
# 기간=1년 → 251행

# =========================================================================
# 등락가 & 등락률 계산 함수
def calculate_change(current_price, prev_close):
    if prev_close == 0:
        return 0, 0
    
    change     = current_price - prev_close
    change_pct = change / prev_close * 100

    return round(change, 2), round(change_pct, 2)

#---------------------------------------------------------------
# 함수 테스트
# change, change_pct = calculate_change(185.0, 180.0)
# print(f'등락가: {change}, 등락률: {change_pct}%')  # 5.0, 2.78%

# change2, change_pct2 = calculate_change(175.0, 180.0)
# print(f'등락가: {change2}, 등락률: {change_pct2}%')  # -5.0, -2.78%

# # 실제 데이터로 테스트
# info = get_stock_info('AAPL')
# if info:
#     c, cp = calculate_change(info['current_price'], info['prev_close'])
#     print(f'AAPL 실제 등락가: {c}, 등락률: {cp}%')

# 등락가: 5.0, 등락률: 2.78%
# 등락가: -5.0, 등락률: -2.78%
# AAPL 실제 등락가: 5.77, 등락률: 2.01%

#============================================================================
# 이동평균 계산 함수
def calculate_moving_average(df, periods=[5,20]):
    result = df.copy()

    for period in periods:
        col_name = f'MA{period}'

        result[col_name] = result['Close'].rolling(window=period).mean()

    return result

#---------------------------------------------------------------------
# 함수 테스트
df = get_stock_history('AAPL', '3달')
df_with_ma = calculate_moving_average(df, periods=[5, 20])

print('컬럼 목록:', df_with_ma.columns.tolist())
print(df_with_ma[['Close', 'MA5', 'MA20']].tail(10))