import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
st.set_page_config(page_title='Trading AI - Research & Paper Signals',layout='wide')
st.title('Trading AI | Research & Paper Signals')
st.caption('Educational research only. Delayed/incomplete market data possible. No live orders or guaranteed predictions.')
symbol=st.text_input('Yahoo Finance symbol (example: RELIANCE.NS)', 'RELIANCE.NS').strip().upper()
period=st.selectbox('Historical period',['6mo','1y','2y'],index=1)
risk=st.number_input('Illustrative account capital (₹)',min_value=1000.,value=100000.,step=1000.)
risk_pct=st.slider('Risk per hypothetical trade (%)',0.1,2.0,1.0,0.1)
@st.cache_data(ttl=900)
def fetch(sym,per):
    x=yf.download(sym,period=per,interval='1d',auto_adjust=True,progress=False)
    if isinstance(x.columns,pd.MultiIndex): x.columns=x.columns.get_level_values(0)
    return x.dropna().copy()
def compute(df):
    d=df.copy(); c=d['Close']; delta=c.diff(); gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean(); rs=gain/loss.replace(0,np.nan)
    d['RSI']=100-100/(1+rs); d['EMA20']=c.ewm(span=20,adjust=False).mean(); d['EMA50']=c.ewm(span=50,adjust=False).mean(); d['MACD']=c.ewm(span=12,adjust=False).mean()-c.ewm(span=26,adjust=False).mean(); d['MACD_signal']=d['MACD'].ewm(span=9,adjust=False).mean()
    tr=pd.concat([(d.High-d.Low),(d.High-c.shift()).abs(),(d.Low-c.shift()).abs()],axis=1).max(axis=1); d['ATR']=tr.ewm(alpha=1/14,adjust=False).mean()
    d['signal']=np.select([(c>d.EMA20)&(d.EMA20>d.EMA50)&(d.RSI.between(50,70))&(d.MACD>d.MACD_signal),(c<d.EMA20)&(d.EMA20<d.EMA50)&(d.RSI.between(30,50))&(d.MACD<d.MACD_signal)],['BULLISH','BEARISH'],default='NO TRADE')
    return d
if st.button('Analyze',type='primary'):
    try:
        raw=fetch(symbol,period)
        if len(raw)<70: st.error('Not enough historical data (need at least 70 daily bars).'); st.stop()
        d=compute(raw); last=d.iloc[-1]; close=float(last.Close); atr=float(last.ATR); signal=last.signal
        st.subheader(f'{symbol}: {signal}'); st.metric('Latest daily close (not live)',f'₹{close:,.2f}'); st.write('Last data date:',str(d.index[-1].date()))
        if signal!='NO TRADE' and np.isfinite(atr) and atr>0:
            stop=close-1.5*atr if signal=='BULLISH' else close+1.5*atr; target=close+3*atr if signal=='BULLISH' else close-3*atr
            qty=int((risk*risk_pct/100)/abs(close-stop)); st.write(f'Illustrative entry at close: ₹{close:.2f} | Stop: ₹{stop:.2f} | Target: ₹{target:.2f} | Reward/risk: 2:1 | Risk-sized quantity: {qty} shares (ignores fees, gaps, slippage and margin).')
            if signal=='BEARISH': st.warning('Bearish is an observation, not a short-sale instruction. Short selling has special restrictions and risks.')
        st.line_chart(d[['Close','EMA20','EMA50']]); st.line_chart(d[['RSI']]); st.dataframe(d[['Close','RSI','MACD','MACD_signal','ATR','signal']].tail(25).round(2))
        st.info('Signals are rule-based, not a trained predictive ML model. Backtest and paper-trade independently before considering real capital. No brokerage integration.')
    except Exception as e: st.error(f'Data/analysis failed: {e}')
