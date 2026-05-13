import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# plotly로 인터랙티브 라인 차트 만들기


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
    

def calculate_moving_average(df, periods=[5,20]):
    result = df.copy()

    for period in periods:
        col_name = f'MA{period}'

        result[col_name] = result['Close'].rolling(window=period).mean()

    return result

#-----------------------------------------------------------------------------

# [1] plotly 탐색
df = get_stock_history('000660.KS', '1달')

fig = go.Figure()       # 빈 도화지 만들기

# Scatter trace: 점/선 차트
fig.add_trace(go.Scatter(
    x = df.index,           # x축: 날짜
    y = df['Close'],        # y축: 종가
    mode = 'lines',         # 'lines', 'markers', 'line+markers'
    name = '종가',
    line = dict(color='royalblue', width=2)
))

fig.update_layout(title='AAPL 종가 (기본차트)', height=400)
# fig.show()

# [2] subplot: 차트를 위아래로 나누는 방법
# rows=2: 2개 행, row_heights: 각 행의 높이 비율
fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.7, 0.3],     # 상단 70%, 하단 30%
    shared_xaxes=True,          # x축 공유 (줌할 때 같이 움직임)
    vertical_spacing=0.05
)

# 상단(row=1): 종가
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='종가'), row=1, col=1)

# 하단(row=2): 거래량
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='거래량'), row=2, col=1)

fig.update_layout(title='종가 + 거래량 서브플롯', height=500)
# fig.show()

#----------------------------------------------------------------------------------
# [3] 가격 라인 차트 함수
# 입력: DataFrame (OHLCV), 티커 심볼, 기간 문자열, 이동평균 표시 여부
# 출력: plotly Figure 객체
# 종가 라인 + 이동평균선(MA5, MA20) 포함
# 상승/하락 색상: 종가 > 시가 → 빨강, 아니면 파랑
def make_price_chart(df, ticker_symbol, period='1달', show_ma=True):
    '''
    종가 라인 차트와 이동평균선을 그립니다.
    df: OHLCV 데이터
    ticker_symbol: 티커 심볼
    period: 기간 문자열
    show_ma: 이동평균선 표시 여부
    '''

    # 이동 평균 계산
    if show_ma:
        df = calculate_moving_average(df, periods=[5, 20])

    # Figure 생성
    fig = go.Figure()

    # 종가 라인 추가
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='종가',
        line=dict(color='#2196F3', width=2)
    ))

    # 이동평균선 추가 (show_ma=True일 때만)
    if show_ma:
        ma_colors = {'MA5': '#FF9800', 'MA20': '#9C27B0'}  # 5일: 주황, 20일: 보라

        for ma_col, color in ma_colors.items():
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[ma_col],
                mode='lines',
                name=ma_col,
                line=dict(color=color, width=1.5, dash='dot')
            ))

    # 레이아웃 설정
    fig.update_layout(
        title=f'{ticker_symbol} 주가 차트 ({period})',
        xaxis_title='날짜',
        yaxis_title='가격',
        height=400,
        hovermode='x unified',
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig

# 테스트
df = get_stock_history('000660.KS', '3달')
fig = make_price_chart(df, '000660.KS', '3달', show_ma=True)
# fig.show()

# [4] 가격 + 거래량 통합 차트
# 가격 차트(상단 70%) + 거래량 차트(하단 30%) 구성
# x축 공유 (하나를 줌하면 다른 것도 같이 줌)
# 거래량 바차트 색상: 상승일 빨강, 하락일 파랑

def make_combined_chart(df, ticker_symbol, period='1달', show_ma=True):
    if show_ma:
        df = calculate_moving_average(df, periods=[5, 20])

    # subplot 생성
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.7, 0.3],
        shared_xaxes=True,
        vertical_spacing=0.05
    )

    # 상단(row=1): 종가 라인
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Close'], mode='lines',
                   name='종가', line=dict(color='#2196F3', width=2)),
        row=1, col=1
    )

    # 상단(row=1): 이동평균선
    if show_ma:
        for ma_col, color in [('MA5', '#FF9800'), ('MA20', '#9C27B0')]:
            fig.add_trace(
                go.Scatter(x=df.index, y=df[ma_col], mode='lines',
                           name=ma_col, line=dict(color=color, width=1.5, dash='dot')),
                row=1, col=1
            )

    # 하단(row=2): 거래량 바차트
    # 상승일(종가 >= 시가)이면 빨강, 하락일이면 파랑
    volume_colors = ['#E53935' if close >= open_ else '#1E88E5'
                     for close, open_ in zip(df['Close'], df['Open'])]
    
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'],
               name='거래량', marker_color=volume_colors,
               showlegend=False),
        row=2, col=1
    )

    # 전체 레이아웃
    fig.update_layout(
        title=f'{ticker_symbol} 차트 ({period})',
        height=550,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    fig.update_yaxes(title_text='가격', row=1, col=1)
    fig.update_yaxes(title_text='거래량', row=2, col=1)

    return fig


# 테스트
df = get_stock_history('TSLA', '3달')
fig = make_combined_chart(df, 'TSLA', '3달', show_ma=True)
# fig.show()


# [5] 여러 종목 비교 차트
# 여러 종목을 같은 차트에 표시
# 시작 시점을 100으로 정규화해서 비교 (주가 단위가 달라 그냥 비교 불가)
# 정규화: (현재가 / 첫날 시작가) × 100
def make_comparison_chart(tickers, period='1달'):
    fig = go.Figure()

    for ticker_symbol in tickers:
        df = get_stock_history(ticker_symbol, period)
        if df is None:
            continue

        # 정규화: 첫 번째 종가를 기준(100)으로 변환
        normalized = df['Close'] / df['Close'].iloc[0] * 100

        fig.add_trace(go.Scatter(
            x=df.index,
            y=normalized,
            mode='lines',
            name=ticker_symbol
        ))

    # 기준선 100 추가 (점선)
    fig.add_hline(y=100, line_dash='dash', line_color='gray',
                  annotation_text='기준선(100)')
    
    fig.update_layout(
        title=f'종목비교 ({period}, 시작가=100 기준)',
        yaxis_title='정규화 가격',
        height=400,
        hovermode='x unified'
    )

    return fig

# 테스트
fig = make_comparison_chart(['AAPL', 'TSLA', 'GOOGL'], '3달')
fig.show()