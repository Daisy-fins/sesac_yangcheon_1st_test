import streamlit as st
import FinanceDataReader as fdr
import mplfinance as mpf
import pandas as pd
from datetime import datetime, timedelta

# KOSPI 종목 리스트 불러오기
@st.cache_data
def get_kospi_stocks():
    try:
        stocks = fdr.StockListing('KOSPI')
        if stocks.empty:
            st.error('KOSPI 종목 리스트를 불러올 수 없습니다.')
            return pd.DataFrame()
        stocks = stocks[['Code', 'Name']]
        stocks = stocks.dropna()
        stocks['display'] = stocks['Code'] + ' : ' + stocks['Name']
        return stocks
    except Exception as e:
        st.error(f'KOSPI 종목 리스트 로딩 중 오류가 발생했습니다: {str(e)}')
        return pd.DataFrame()

stocks = get_kospi_stocks()

if stocks.empty:
    st.stop()

# 종목 selectbox 옵션 생성
stock_options = stocks['display'].tolist()
stock_code_map = dict(zip(stocks['display'], stocks['Code']))
stock_name_map = dict(zip(stocks['Code'], stocks['Name']))

# MplFinance 스타일 옵션
try:
    mpf_styles = mpf.available_styles()
except Exception as e:
    st.error(f'MplFinance 스타일을 불러올 수 없습니다: {str(e)}')
    mpf_styles = ['default']

# 사이드바 폼
with st.sidebar.form(key='input_form', clear_on_submit=False):
    st.header('입력값 설정')
    selected_stock_display = st.selectbox('종목 선택', stock_options, index=0)
    selected_code = stock_code_map[selected_stock_display]
    period = st.slider('기간(일)', min_value=5, max_value=730, value=30, step=1)
    selected_style = st.selectbox('차트 스타일', mpf_styles, index=0)
    show_volume = st.checkbox('거래량 시각화', value=False)
    submitted = st.form_submit_button('제출')

# 메인 화면
st.title('📈 주가 데이터 시각화')

selected_name = stock_name_map[selected_code]
st.markdown(f"📌 현재 차트: {selected_name}")
st.markdown("📌 이동평균선(mav): :green[5일], :blue[20일], :orange[60일]")

# 데이터 불러오기
try:
    end_date = datetime.today()
    start_date = end_date - timedelta(days=period)
    
    data = fdr.DataReader(selected_code, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    
    if data.empty:
        st.warning('해당 기간에 데이터가 없습니다.')
    else:
        # 캔들차트 그리기
        try:
            mav = (5, 20, 60)
            mc = mpf.make_marketcolors(up='red', down='blue', edge='inherit', wick='inherit', volume='gray') # inherit: 캔들 색상과 일치, gray: 막대 색상을 고정 색상으로 지정
            s = mpf.make_mpf_style(base_mpf_style=selected_style, marketcolors=mc)
            
            kwargs = dict(type='candle', mav=mav, style=s, figsize=(10, 6), returnfig=True)
            if show_volume:
                kwargs['volume'] = True
            
            fig, axes = mpf.plot(data, **kwargs, warn_too_much_data=10000)
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f'차트 생성 중 오류가 발생했습니다: {str(e)}')
            
except Exception as e:
    st.error(f'주가 데이터를 불러오는 중 오류가 발생했습니다: {str(e)}')

    
